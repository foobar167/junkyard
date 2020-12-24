# -*- coding: utf-8 -*-
import operator
import tkinter as tk

from .gui_canvas import CanvasImage

class Rectangles(CanvasImage):
    """ Class of Rectangles. Inherit CanvasImage class """
    def __init__(self, placeholder, path):
        """ Initialize the Rectangles """
        CanvasImage.__init__(self, placeholder, path)  # call __init__ of the CanvasImage class
        self.canvas.bind('<ButtonPress-1>', self.start_rect)  # start new rectangle
        self.canvas.bind('<ButtonRelease-1>', self.finish_rect)  # finish new rectangle
        self.canvas.bind('<ButtonRelease-3>', self.popup)  # call popup menu
        self.canvas.bind('<Motion>', self.motion)  # handle mouse motion
        self.canvas.bind('<Delete>', lambda event: self.delete_rect())  # delete selected rectangle
        # Create a popup menu for Rectangles
        self.hold_menu1 = False  # popup menu is closed
        self.hold_menu2 = False
        self.menu = tk.Menu(self.canvas, tearoff=0)
        self.menu.add_command(label='Delete', command=self.delete_rect, accelerator=u'Delete')
        # Rectangle parameters
        self.width_line = 2  # lines width
        self.dash = (1, 1)  # dash pattern
        self.color_roi = {'draw': 'red',  # draw roi color
                          'point': 'blue',  # point roi color
                          'back': 'yellow',  # background roi color
                          'stipple': 'gray12'}  # stipple value for roi
        self.current_rect = None  # current rectangle to draw on the canvas
        self.current_rect_coords = None  # current rectangle coordinates
        self.tag_roi = 'roi'  # roi tag
        self.tag_const = 'rect'  # constant tag for rectangle
        self.tag_poly_line = 'poly_line'  # edge of the rectangle
        self.selected_rect = []  # selected rectangles
        self.roi_dict = {}  # dictionary of all rectangles and their coords on the canvas

    def start_rect(self, event):
        """ Start to draw rectangle """
        if self.hold_menu2:  # popup menu is opened
            self.hold_menu2 = False  # popup menu closes automatically
            self.motion(event)  # motion event for popup menu
            return  # exit from drawing new rectangle
        self.motion(event)  # generate motion event. It's needed for menu bar, bug otherwise!
        x = self.canvas.canvasx(event.x)  # get coordinates of the event on the canvas
        y = self.canvas.canvasy(event.y)
        if self.outside(x, y): return  # starting point is out of scope
        # Start to draw current rectangle
        self.current_rect = self.canvas.create_rectangle(
            (x, y, x, y), width=self.width_line, outline=self.color_roi['draw'])
        self.current_rect_coords = (x, y)  # save (x, y)

    def finish_rect(self, event):
        """ Finish to draw rectangle """
        if not self.current_rect:
            return  # there is no current rectangle
        if ' '.join(map(str, self.dash)) == self.canvas.itemcget(self.current_rect, 'dash'):
            self.delete_current_rect()
            return  # release button is out of scope
        # Get rectangle coordinates on the zoomed image
        bbox1 = self.canvas.coords(self.current_rect)  # get rectangle area
        if bbox1[0] == bbox1[2] or bbox1[1] == bbox1[3]:
            self.delete_current_rect()
            return  # rectangle has no area, so exit and don't draw it
        bbox2 = self.canvas.coords(self.container)  # get image area
        # Get rectangle coordinates on the image
        x1 = int((bbox1[0] - bbox2[0]) / self.imscale)
        y1 = int((bbox1[1] - bbox2[1]) / self.imscale)
        x2 = int((bbox1[2] - bbox2[0]) / self.imscale)
        y2 = int((bbox1[3] - bbox2[1]) / self.imscale)
        bbox = (x1, y1, x2, y2)  # coords on the image
        self.draw_rect(bbox1, bbox)  # draw rectangle
        self.delete_current_rect()

    def delete_current_rect(self):
        """ Delete current rectangle """
        self.canvas.delete(self.current_rect)  # delete from the canvas
        self.current_rect = None
        self.current_rect_coords = None

    def draw_rect(self, bbox1, bbox2):
        """ Draw rectangle.
            bbox1 - rectangle coordinates on the canvas.
            bbox2 - rectangle coordinates on the image. """
        # Create rectangle unique ID tag
        tag_uid = '{}-{}-{}-{}'.format(bbox2[0], bbox2[1], bbox2[2], bbox2[3])
        if tag_uid not in self.roi_dict:  # save only unique rectangles with different coords
            # Create rectangle. 2nd tag is ALWAYS a unique tag ID + constant string.
            self.canvas.create_rectangle(bbox1, fill=self.color_roi['point'],
                                         stipple=self.color_roi['stipple'],
                                         width=0, state='hidden',
                                         tags=(self.tag_roi, tag_uid + self.tag_const))
            # Create polyline. 2nd tag is ALWAYS a unique tag ID.
            vertices = [(bbox1[0], bbox1[1]), (bbox1[2], bbox1[1]),
                        (bbox1[2], bbox1[3]), (bbox1[0], bbox1[3]),]
            for j in range(-1, len(vertices) - 1):
                self.canvas.create_line(vertices[j], vertices[j + 1], width=self.width_line,
                                        fill=self.color_roi['back'],
                                        tags=(self.tag_poly_line, tag_uid))
            self.roi_dict[tag_uid] = bbox2  # remember rectangle coordinates in the dictionary
            # Print rectangles number into console
            print('Images: {n}'.format(n=len(self.roi_dict)) + (20 * ' ') + '\r', end='')

    def popup(self, event):
        """ Popup menu """
        self.motion(event)  # select rectangle with popup menu explicitly to be sure it is selected
        if self.selected_rect:  # show popup menu only for selected rectangle
            self.hold_menu1 = True  # popup menu is opened
            self.hold_menu2 = True
            self.menu.post(event.x_root, event.y_root)  # show popup menu
            self.hold_menu1 = False  # popup menu is closed

    def motion(self, event):
        """ Track mouse position over the canvas """
        if self.hold_menu1: return  # popup menu is opened
        # Redraw current rectangle if it exists
        if self.current_rect:
            x = self.canvas.canvasx(event.x)  # get coordinates of the event on the canvas
            y = self.canvas.canvasy(event.y)
            if self.outside(x, y):  # outside of the canvas
                self.canvas.itemconfigure(self.current_rect, dash=self.dash)  # set dashed line
            else:
                self.canvas.itemconfigure(self.current_rect, dash='')  # set solid line
            # Relocate (change) rectangle
            self.canvas.coords(self.current_rect, (min(self.current_rect_coords[0], x),
                                                   min(self.current_rect_coords[1], y),
                                                   max(self.current_rect_coords[0], x),
                                                   max(self.current_rect_coords[1], y),))
            self.canvas.lift(self.current_rect)  # set roi into foreground
        # Handle rectangles on the canvas
        self.deselect_rect()  # change color and zeroize selected rectangle
        self.select_rect()  # change color and select rectangle

    def select_rect(self):
        """ Select and change color of the current roi object """
        i = self.canvas.find_withtag('current')  # id of the current object
        tags = self.canvas.gettags(i)  # get tags of the current object
        if self.tag_poly_line in tags:  # if it's a polyline. 2nd tag is ALWAYS a unique tag ID
            j = tags[1] + self.tag_const  # unique tag of the rectangle
            self.canvas.itemconfigure(tags[1], fill=self.color_roi['point'])  # select lines
            self.canvas.itemconfigure(j, state='normal')  # show rectangle
            self.selected_rect.append(tags[1])  # remember 2nd unique tag_id

    def deselect_rect(self):
        """ Deselect current roi object """
        if not self.selected_rect: return  # selected rectangles list is empty
        for i in self.selected_rect:
            j = i + self.tag_const  # unique tag of the rectangle
            self.canvas.itemconfigure(i, fill=self.color_roi['back'])  # deselect lines
            self.canvas.itemconfigure(j, state='hidden')  # hide rectangle
        self.selected_rect.clear()  # clear the list

    def delete_rect(self):
        """ Delete selected rectangle """
        if self.selected_rect:  # delete selected rectangle
            for i in self.selected_rect:
                j = i + self.tag_const  # unique tag of the rectangle
                del(self.roi_dict[i])  # delete ROI from the dictionary of all rectangles
                self.canvas.delete(i)  # delete lines
                self.canvas.delete(j)  # delete rectangle
            self.selected_rect.clear()  # clear selection list
            # print rectangles number into console
            print('Images: {n}'.format(n=len(self.roi_dict)) + (20 * ' ') + '\r', end='')
            self.hold_menu2 = False  # popup menu is closed

    def delete_all(self):
        """ Delete all rectangles from the canvas and clear variables """
        self.canvas.delete(self.tag_roi)  # delete all rectangles
        self.canvas.delete(self.tag_poly_line)  # delete all poly-lines
        self.selected_rect.clear()  # clear selection list
        self.hold_menu2 = False  # popup menu is closed
        self.roi_dict.clear()  # clear dictionary of ROI

    def reset(self, roi):
        """ Reset ROI and holes on the image """
        self.delete_all()  # delete old rectangles
        bbox2 = self.canvas.coords(self.container)  # get canvas coordinates
        for bbox in roi:  # draw roi rectangles
            bbox1 = (int(bbox[0] * self.imscale) + bbox2[0],
                     int(bbox[1] * self.imscale) + bbox2[1],
                     int(bbox[2] * self.imscale) + bbox2[0],
                     int(bbox[3] * self.imscale) + bbox2[1])
            self.draw_rect(bbox1, bbox)
