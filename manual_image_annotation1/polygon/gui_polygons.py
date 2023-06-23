# -*- coding: utf-8 -*-
import uuid
import tkinter as tk

from .gui_canvas import CanvasImage

class Polygons(CanvasImage):
    """ Class of Polygons. Inherit CanvasImage class """
    def __init__(self, placeholder, path, roll_size):
        """ Initialize the Polygons """
        CanvasImage.__init__(self, placeholder, path)  # call __init__ of the CanvasImage class
        self.canvas.bind('<ButtonPress-1>', self.set_edge)  # set new edge
        self.canvas.bind('<ButtonRelease-3>', self.popup)  # call popup menu
        self.canvas.bind('<Motion>', self.motion)  # handle mouse motion
        self.canvas.bind('<Delete>', lambda event: self.delete_poly())  # delete selected polygon
        # Create a popup menu for Polygons
        self.hold_menu1 = False  # popup menu is closed
        self.hold_menu2 = False
        self.menu = tk.Menu(self.canvas, tearoff=0)
        self.menu.add_command(label='Delete', command=self.delete_poly, accelerator=u'Delete')
        # Polygon parameters
        self.roi = True  # is it a ROI or hole
        self.rect = True  # show / hide rolling window rectangle
        self.roll_size = roll_size  # size of the rolling window
        self.width_line = 6  # lines width
        self.roll_rect = self.canvas.create_rectangle((0, 0, 0, 0), width=self.width_line,
                                                      state=u'hidden')
        self.dash = (1, 1)  # dash pattern
        self.color_back_hole = 'cyan'  # draw hole color
        self.color_back_roi = 'yellow'  # draw roi color
        self.color_hole = {'draw'   : 'magenta',  # draw hole color
                           'point'  : '#8B0000',  # point hole color
                           'back'   : self.color_back_hole,  # background hole color
                           'stipple': 'gray50'}   # stipple value for hole
        self.color_roi =  {'draw'   : 'red',      # draw roi color
                           'point'  : 'blue',     # point roi color
                           'back'   : self.color_back_roi,  # background roi color
                           'stipple': 'gray12'}   # stipple value for roi
        self.tag_curr_edge_start = '1st_edge'  # starting edge of the current polygon
        self.tag_curr_edge = 'edge'  # edges of the polygon
        self.tag_curr_edge_id = 'edge_id'  # part of unique ID of the current edge
        self.tag_roi = 'roi'  # roi tag
        self.tag_hole = 'hole'  # hole tag
        self.tag_const = 'poly'  # constant tag for polygon
        self.tag_poly_line = 'poly_line'  # edge of the polygon
        self.tag_curr_circle = 'circle'  # sticking circle tag for the current polyline
        self.radius_stick = 10  # distance where line sticks to the polygon's staring point
        self.radius_circle = 3  # radius of the sticking circle
        self.edge = None  # current edge of the new polygon
        self.polygon = []  # vertices of the current (drawing, red) polygon
        self.selected_poly = []  # selected polygons
        self.roi_dict = {}  # dictionary of all roi polygons and their coords on the canvas image
        self.hole_dict = {}  # dictionary of all holes and their coordinates on the canvas image

    def set_edge(self, event):
        """ Set edge of the polygon """
        if self.hold_menu2:  # popup menu was opened
            self.hold_menu2 = False
            self.motion(event)  # motion event for popup menu
            return
        self.motion(event)  # generate motion event. It's needed for menu bar, bug otherwise!
        x = self.canvas.canvasx(event.x)  # get coordinates of the event on the canvas
        y = self.canvas.canvasy(event.y)
        if self.edge and ' '.join(map(str, self.dash)) == self.canvas.itemcget(self.edge, 'dash'):
            return  # the edge is out of scope or self-crossing with other edges
        elif not self.edge and self.outside(x, y):
            return  # starting point is out of scope
        color = self.color_roi if self.roi else self.color_hole  # set color palette
        if not self.edge:  # start drawing polygon
            self.draw_edge(color, x, y, self.tag_curr_edge_start)
            # Draw sticking circle
            self.canvas.create_oval(x - self.radius_circle, y - self.radius_circle,
                                    x + self.radius_circle, y + self.radius_circle,
                                    width=0, fill=color['draw'],
                                    tags=(self.tag_curr_edge, self.tag_curr_circle))
        else:  # continue drawing polygon
            x1, y1, x2, y2 = self.canvas.coords(self.tag_curr_edge_start)  # get coords of the 1st edge
            x3, y3, x4, y4 = self.canvas.coords(self.edge)  # get coordinates of the current edge
            if x4 == x1 and y4 == y1:  # finish drawing polygon
                if len(self.polygon) > 2:  # draw polygon on the zoomed image canvas
                    if self.roi:  # it's a ROI polygon
                        d = self.roi_dict
                        tag = self.tag_roi
                    else:  # it's a hole polygon
                        d = self.hole_dict
                        tag = self.tag_hole
                    self.draw_polygon(self.polygon, color, tag, d)
                self.delete_edges()  # delete edges of drawn polygon
            else:
                self.draw_edge(color, x, y)  # continue drawing polygon, set new edge

    def draw_polygon(self, polygon, color, tag, dictionary):
        """ Draw polygon on the canvas """
        # Calculate coordinates of vertices on the zoomed image
        bbox = self.canvas.coords(self.container)  # get image area
        vertices = list(map((lambda i: (i[0] * self.imscale + bbox[0],
                                        i[1] * self.imscale + bbox[1])), polygon))
        # Create identification tag
        tag_uid = uuid.uuid4().hex  # unique ID
        # Create polygon. 2nd tag is ALWAYS a unique tag ID + constant string.
        self.canvas.create_polygon(vertices, fill=color['point'],
                                   stipple=color['stipple'], width=0, state='hidden',
                                   tags=(tag, tag_uid + self.tag_const))
        # Create polyline. 2nd tag is ALWAYS a unique tag ID.
        for j in range(-1, len(vertices) - 1):
            self.canvas.create_line(vertices[j], vertices[j + 1], width=self.width_line,
                                    fill=color['back'], tags=(self.tag_poly_line, tag_uid))
        # Remember ROI / hole in the dictionary of all ROIs / holes
        dictionary[tag_uid] = polygon.copy()

    def draw_edge(self, color, x, y, tags=None):
        """ Draw edge of the polygon """
        if len(self.polygon) > 1:
            x1, y1, x2, y2 = self.canvas.coords(self.edge)
            if x1 == x2 and y1 == y2:
                return  # don't draw edge in the same point, otherwise it'll be self-intersection
        curr_edge_id = self.tag_curr_edge_id + str(len(self.polygon))  # ID of the edge in the polygon
        self.edge = self.canvas.create_line(x, y, x, y, fill=color['draw'], width=self.width_line,
                                            tags=(tags, self.tag_curr_edge, curr_edge_id,))
        bbox = self.canvas.coords(self.container)  # get image area
        x1 = round((x - bbox[0]) / self.imscale)  # get real (x,y) on the image without zoom
        y1 = round((y - bbox[1]) / self.imscale)
        self.polygon.append((x1, y1))  # add new vertex to the list of polygon vertices

    def popup(self, event):
        """ Popup menu """
        self.motion(event)  # select polygon with popup menu explicitly to be sure it is selected
        if self.selected_poly:  # show popup menu only for selected polygon
            self.hold_menu1 = True  # popup menu is opened
            self.hold_menu2 = True
            self.menu.post(event.x_root, event.y_root)  # show popup menu
            self.hold_menu1 = False  # popup menu is closed

    def motion(self, event):
        """ Track mouse position over the canvas """
        if self.hold_menu1: return  # popup menu is opened
        x = self.canvas.canvasx(event.x)  # get coordinates of the event on the canvas
        y = self.canvas.canvasy(event.y)
        if self.edge:  # relocate edge of the drawn polygon
            x1, y1, x2, y2 = self.canvas.coords(self.tag_curr_edge_start)  # get coordinates of the 1st edge
            x3, y3, x4, y4 = self.canvas.coords(self.edge)  # get coordinates of the current edge
            dx = x - x1
            dy = y - y1
            # Set new coordinates of the edge
            if self.radius_stick * self.radius_stick > dx * dx + dy * dy:  # sticking radius
                self.canvas.coords(self.edge, x3, y3, x1, y1)  # stick to the beginning
                self.set_dash(x1, y1)  # set dash for edge segment
            else:  # follow the mouse
                self.canvas.coords(self.edge, x3, y3, x, y)  # follow the mouse movements
                self.set_dash(x, y)  # set dash for edge segment
        # Handle polygons on the canvas
        self.deselect_poly()  # change color and zeroize selected polygon
        self.select_poly()  # change color and select polygon
        if self.rect:  # show / hide rolling window rectangle
            w = int(self.roll_size[0] * self.imscale) >> 1
            h = int(self.roll_size[1] * self.imscale) >> 1
            self.canvas.coords(self.roll_rect, (x-w, y-h, x+w, y+h))  # relocate rolling window
            color = self.color_back_roi if self.roi else self.color_back_hole
            self.canvas.itemconfigure(self.roll_rect, state='normal', outline=color)  # show it
        else:
            self.canvas.itemconfigure(self.roll_rect, state='hidden')  # hide rolling window

    def set_dash(self, x, y):
        """ Set dash for edge segment """
        # If outside of the image or polygon self-intersection is occurred
        if self.outside(x, y) or self.polygon_selfintersection():
            self.canvas.itemconfigure(self.edge, dash=self.dash)  # set dashed line
        else:
            self.canvas.itemconfigure(self.edge, dash='')  # set solid line

    def deselect_poly(self):
        """ Deselect current roi object """
        if not self.selected_poly: return  # selected polygons list is empty
        for i in self.selected_poly:
            j = i + self.tag_const  # unique tag of the polygon
            color = self.color_roi if self.is_roi(j) else self.color_hole  # get color palette
            self.canvas.itemconfigure(i, fill=color['back'])  # deselect lines
            self.canvas.itemconfigure(j, state='hidden')  # hide figure
        self.selected_poly.clear()  # clear the list

    def select_poly(self):
        """ Select and change color of the current roi object """
        if self.edge: return  # new polygon is being created (drawn) right now
        i = self.canvas.find_withtag('current')  # id of the current object
        tags = self.canvas.gettags(i)  # get tags of the current object
        if self.tag_poly_line in tags:  # If it's a polyline. 2nd tag is ALWAYS a unique tag ID
            j = tags[1] + self.tag_const  # unique tag of the polygon
            color = self.color_roi if self.is_roi(j) else self.color_hole  # get color palette
            self.canvas.itemconfigure(tags[1], fill=color['point'])  # select lines through 2nd tag
            self.canvas.itemconfigure(j, state='normal')  # show polygon
            self.selected_poly.append(tags[1])  # remember 2nd unique tag_id

    def is_roi(self, tag):
        """ Return True if polygon is ROI. Return False if polygon is hole """
        tags = self.canvas.gettags(tag)
        if self.tag_roi in tags:
            return True
        return False

    def redraw_figures(self):
        """ Overwritten method. Redraw sticking circle for the wheel event """
        bbox = self.canvas.coords(self.tag_curr_circle)
        if bbox:  # radius of sticky circle is unchanged during zoom
            cx = (bbox[0] + bbox[2]) / 2  # center of the circle
            cy = (bbox[1] + bbox[3]) / 2
            self.canvas.coords(self.tag_curr_circle,
                               cx - self.radius_circle, cy - self.radius_circle,
                               cx + self.radius_circle, cy + self.radius_circle)

    def delete_edges(self):
        """ Delete edges of drawn polygon """
        if self.edge:  # if polygon is being drawing, delete it
            self.edge = None  # delete all edges and set current edge to None
            self.canvas.delete(self.tag_curr_edge)  # delete all edges
            self.polygon.clear()  # remove all items from vertices list

    def delete_poly(self):
        """ Delete selected polygon """
        self.delete_edges()  # delete edges of drawn polygon
        if self.selected_poly:  # delete selected polygon
            for i in self.selected_poly:
                j = i + self.tag_const  # unique tag of the polygon
                if self.is_roi(j):
                    del(self.roi_dict[i])  # delete ROI from the dictionary of all ROIs
                else:
                    del(self.hole_dict[i])  # delete hole from the dictionary of all holes
                self.canvas.delete(i)  # delete lines
                self.canvas.delete(j)  # delete polygon
            self.selected_poly.clear()  # clear selection list
            self.hold_menu2 = False  # popup menu is closed

    def delete_all(self):
        """ Delete all polygons from the canvas and clear variables """
        self.delete_edges()  # delete edges of drawn polygon
        self.canvas.delete(self.tag_roi)  # delete all ROI
        self.canvas.delete(self.tag_hole)  # delete all holes
        self.canvas.delete(self.tag_poly_line)  # delete all polygon lines
        self.selected_poly.clear()  # clear selection list
        self.hold_menu2 = False  # popup menu is closed
        self.roi_dict.clear()  # clear dictionary of ROI
        self.hole_dict.clear()  # clear dictionary of holes

    def reset(self, roi, holes):
        """ Reset ROI and holes on the image """
        self.delete_all()  # delete old polygons
        for polygon in roi:  # draw roi polygons
            self.draw_polygon(polygon, self.color_roi, self.tag_roi, self.roi_dict)
        for polygon in holes:  # draw hole polygons
            self.draw_polygon(polygon, self.color_hole, self.tag_hole, self.hole_dict)

    @staticmethod
    def orientation(p1, p2, p3):
        """ Find orientation of ordered triplet (p1, p2, p3). Returns following values:
             0 --> p1, p2 and p3 are collinear
            -1 --> clockwise
             1 --> counterclockwise """
        val = (p2[0] - p1[0]) * (p3[1] - p2[1]) - (p2[1] - p1[1]) * (p3[0] - p2[0])
        if   val < 0: return -1  # clockwise
        elif val > 0: return  1  # counterclockwise
        else:         return  0  # collinear

    @staticmethod
    def on_segment(p1, p2, p3):
        """ Given three collinear points p1, p2, p3, the function checks
            if point p2 lies on line segment p1-p3 """
        # noinspection PyChainedComparisons
        if p2[0] <= max(p1[0], p3[0]) and p2[0] >= min(p1[0], p3[0]) and \
           p2[1] <= max(p1[1], p3[1]) and p2[1] >= min(p1[1], p3[1]):
            return True
        return False

    def intersect(self, p1, p2, p3, p4):
        """ Return True if line segments p1-p2 and p3-p4 intersect, otherwise return False """
        # Find 4 orientations
        o1 = self.orientation(p1, p2, p3)
        o2 = self.orientation(p1, p2, p4)
        o3 = self.orientation(p3, p4, p1)
        o4 = self.orientation(p3, p4, p2)
        # General case
        if o1 != o2 and o3 != o4: return True  # segments intersect
        # Segments p1-p2 and p3-p4 are collinear
        if o1 == o2 == 0:
            # p3 lies on segment p1-p2
            if self.on_segment(p1, p3, p2): return True
            # p4 lies on segment p1-p2
            if self.on_segment(p1, p4, p2): return True
            # p1 lies on segment p3-p4
            if self.on_segment(p3, p1, p4): return True
        return False  # doesn't intersect

    def penultimate_intersect(self, p1, p2, p3):
        """ Check penultimate (last but one) edge,
            where p1 and p4 coincide with the current edge """
        if self.orientation(p1, p2, p3) == 0 and not self.on_segment(p3, p1, p2):
            return True
        else:
            return False

    def first_intersect(self, p1, p2, p3, p4):
        """ Check the 1st edge, where points p2 and p3 CAN coincide """
        if p2[0] == p3[0] and p2[1] == p3[1]: return False  # p2 and p3 coincide -- this is OK
        if p1[0] == p3[0] and p1[1] == p3[1]: return False  # there is only 1 edge
        # There is only 2 edges
        if p1[0] == p4[0] and p1[1] == p4[1]: return self.penultimate_intersect(p1, p2, p3)
        return self.intersect(p1, p2, p3, p4)  # General case

    def polygon_selfintersection(self):
        """ Check if polygon has self-intersections """
        x1, y1, x2, y2 = self.canvas.coords(self.edge)  # get coords of the current edge
        for i in range(1, len(self.polygon)-2):  # don't include the 1st ant the last 2 edges
            x3, y3, x4, y4 = self.canvas.coords(self.tag_curr_edge_id + str(i))
            if self.intersect((x1, y1), (x2, y2), (x3, y3), (x4, y4)): return True
        # Check penultimate (last but one) edge, where points p1 and p4 coincide
        j = len(self.polygon) - 2
        if j > 0:  # 2 or more edges
            x3, y3, x4, y4 = self.canvas.coords(self.tag_curr_edge_id + str(j))
            if self.penultimate_intersect((x1, y1), (x2, y2), (x3, y3)): return True
        # Check the 1st edge, where points p2 and p3 CAN coincide
        x3, y3, x4, y4 = self.canvas.coords(self.tag_curr_edge_start)
        if self.first_intersect((x1, y1), (x2, y2), (x3, y3), (x4, y4)): return True
        return False  # there is no self-intersections in the polygon
