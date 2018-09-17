# -*- coding: utf-8 -*-
import tkinter as tk

from .gui_canvas import CanvasImage

class Rectangles(CanvasImage):
    """ Class of Rectangles. Inherit CanvasImage class """
    def __init__(self, placeholder, path, rect_size):
        """ Initialize the Rectangles """
        CanvasImage.__init__(self, placeholder, path)  # call __init__ of the CanvasImage class
        self.canvas.bind('<space>', self.set_rect)  # set new rectangle with a spacebar key press
        self.canvas.bind('<ButtonPress-1>', self.set_rect)  # set new rectangle
        self.canvas.bind('<ButtonRelease-3>', self.popup)  # call popup menu
        self.canvas.bind('<Motion>', self.motion)  # handle mouse motion
        self.canvas.bind('<Delete>', lambda event: self.delete_rect())  # delete selected rectangle
        # Create a popup menu for Rectangles
        self.hold_menu1 = False  # popup menu is closed
        self.hold_menu2 = False
        self.menu = tk.Menu(self.canvas, tearoff=0)
        self.menu.add_command(label='Delete', command=self.delete_rect, accelerator=u'Delete')
        # Rectangle parameters
        self.rect_size = rect_size  # size of the rolling window
        self.width_line = 2  # lines width
        self.dash = (1, 1)  # dash pattern
        self.color_roi = {'draw'   : 'red',     # draw roi color
                          'point'  : 'blue',    # point roi color
                          'back'   : 'yellow',  # background roi color
                          'stipple': 'gray12'}  # stipple value for roi
        self.rect = self.canvas.create_rectangle((0, 0, 0, 0), width=self.width_line,
                                                 dash=self.dash, outline=self.color_roi['draw'])
        self.tag_roi = 'roi'  # roi tag
        self.tag_const = 'rect'  # constant tag for rectangle
        self.tag_poly_line = 'poly_line'  # edge of the rectangle
        self.selected_rect = []  # selected rectangles
        self.roi_dict = {}  # dictionary of all roi rectangles and their top left coords on the canvas

    def set_rect(self, event):
        """ Set rectangle """
        if self.hold_menu2:  # popup menu was opened
            self.hold_menu2 = False
            self.motion(event)  # motion event for popup menu
            return
        self.motion(event)  # generate motion event. It's needed for menu bar, bug otherwise!
        if ' '.join(map(str, self.dash)) == self.canvas.itemcget(self.rect, 'dash'):
            return  # rectangle is out of scope
        # Calculate coordinates of rectangle top left corner on the zoomed image
        bbox1 = self.canvas.coords(self.container)  # get image area
        bbox2 = self.canvas.coords(self.rect)  # get rectangle area
        x = int((bbox2[0] - bbox1[0]) / self.imscale)  # get (x,y) of top left corner on the image
        y = int((bbox2[1] - bbox1[1]) / self.imscale)
        self.draw_rect(bbox2, (x, y))

    def draw_rect(self, bbox, point):
        """ Draw rectangle """
        # Create identification tag
        tag_uid = "{x}-{y}".format(x=point[0], y=point[1])  # unique ID
        if tag_uid not in self.roi_dict:
            # Create rectangle. 2nd tag is ALWAYS a unique tag ID + constant string.
            self.canvas.create_rectangle(bbox, fill=self.color_roi['point'],
                                         stipple=self.color_roi['stipple'], width=0, state='hidden',
                                         tags=(self.tag_roi, tag_uid + self.tag_const))
            # Create polyline. 2nd tag is ALWAYS a unique tag ID.
            vertices = [(bbox[0], bbox[1]), (bbox[2], bbox[1]), (bbox[2], bbox[3]), (bbox[0], bbox[3])]
            for j in range(-1, len(vertices) - 1):
                self.canvas.create_line(vertices[j], vertices[j + 1], width=self.width_line,
                                        fill=self.color_roi['back'], tags=(self.tag_poly_line, tag_uid))
            self.roi_dict[tag_uid] = point  # remember top left corner in the dictionary
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
        x = self.canvas.canvasx(event.x)  # get coordinates of the event on the canvas
        y = self.canvas.canvasy(event.y)
        w = int(self.rect_size[0] * self.imscale) >> 1
        h = int(self.rect_size[1] * self.imscale) >> 1
        bbox = self.canvas.coords(self.container)  # get image area
        if bbox[0] + w <= x < bbox[2] - w and bbox[1] + h <= y < bbox[3] - h:
            self.canvas.itemconfigure(self.rect, dash='')  # set solid line
        else:
            self.canvas.itemconfigure(self.rect, dash=self.dash)  # set dashed line
        self.canvas.coords(self.rect, (x - w, y - h, x + w, y + h))  # relocate rectangle
        self.canvas.lift(self.rect)  # set roi into foreground
        # Handle rectangles on the canvas
        self.deselect_rect()  # change color and zeroize selected rectangle
        self.select_rect()  # change color and select rectangle

    def deselect_rect(self):
        """ Deselect current roi object """
        if not self.selected_rect: return  # selected rectangles list is empty
        for i in self.selected_rect:
            j = i + self.tag_const  # unique tag of the rectangle
            self.canvas.itemconfigure(i, fill=self.color_roi['back'])  # deselect lines
            self.canvas.itemconfigure(j, state='hidden')  # hide rectangle
        self.selected_rect.clear()  # clear the list

    def select_rect(self):
        """ Select and change color of the current roi object """
        i = self.canvas.find_withtag('current')  # id of the current object
        tags = self.canvas.gettags(i)  # get tags of the current object
        if self.tag_poly_line in tags:  # if it's a polyline. 2nd tag is ALWAYS a unique tag ID
            j = tags[1] + self.tag_const  # unique tag of the rectangle
            self.canvas.itemconfigure(tags[1], fill=self.color_roi['point'])  # select lines
            self.canvas.itemconfigure(j, state='normal')  # show rectangle
            self.selected_rect.append(tags[1])  # remember 2nd unique tag_id

    def delete_rect(self):
        """ Delete selected rectangle """
        if self.selected_rect:  # delete selected rectangle
            for i in self.selected_rect:
                j = i + self.tag_const  # unique tag of the rectangle
                del(self.roi_dict[i])  # delete ROI from the dictionary of all rectangles
                self.canvas.delete(i)  # delete lines
                self.canvas.delete(j)  # delete rectangle
            self.selected_rect.clear()  # clear selection list
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
        bbox1 = self.canvas.coords(self.container)  # get image area
        for point in roi:  # draw roi rectangles
            bbox2 = (int(point[0] * self.imscale) + bbox1[0],
                     int(point[1] * self.imscale) + bbox1[1],
                     int((point[0] + self.rect_size[0]) * self.imscale) + bbox1[0],
                     int((point[1] + self.rect_size[1]) * self.imscale) + bbox1[1])
            self.draw_rect(bbox2, point)
