# Drawing polygon on the image
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk


class AutoScrollbar(ttk.Scrollbar):
    """ A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager """
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with the widget ' + self.__class__.__name__)

    def place(self, **kw):
        raise tk.TclError('Cannot use place with the widget ' + self.__class__.__name__)


class CanvasImage:
    """ Image on the canvas """
    def __init__(self, parent, impath):
        """ Initialize the canvas """
        # Create frame container for the canvas and scrolling bars. Make it expandable
        self.imframe = ttk.Frame(parent)  # parent of the CanvasImage objects
        # Vertical and horizontal scrollbars for canvas
        vbar = AutoScrollbar(self.imframe, orient='vertical')
        hbar = AutoScrollbar(self.imframe, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')
        # Create canvas and put image on it
        self.canvas = tk.Canvas(self.imframe, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.canvas.update()  # wait till canvas is created
        vbar.configure(command=self.scroll_y)  # bind scrollbars to the canvas
        hbar.configure(command=self.scroll_x)
        # Bind events to the Canvas
        self.canvas.bind('<Configure>',     self.show_image)  # canvas is resized
        self.canvas.bind('<ButtonPress-3>', self.move_from)
        self.canvas.bind('<B3-Motion>',     self.move_to)
        self.canvas.bind('<MouseWheel>',    self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',      self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>',      self.wheel)  # only with Linux, wheel scroll up
        self.image = Image.open(impath)  # open image
        self.im_width, self.im_height = self.image.size
        self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.im_width, self.im_height, width=0)
        self.show_image()  # show image on the screen
        self.canvas.focus_set()  # set focus on the canvas

    def scroll_y(self, *args):
        """ Scroll canvas vertically and redraw the image """
        self.canvas.yview(*args)  # scroll vertically
        self.show_image()  # redraw the image

    def scroll_x(self, *args):
        """ Scroll canvas horizontally and redraw the image """
        self.canvas.xview(*args)  # scroll horizontally
        self.show_image()  # redraw the image

    def show_image(self, event=None):
        """ Show image on the canvas """
        box_image = self.canvas.coords(self.container)  # get image area
        box_canvas = (self.canvas.canvasx(0),  # get visible area of the canvas
                      self.canvas.canvasy(0),
                      self.canvas.canvasx(self.canvas.winfo_width()),
                      self.canvas.canvasy(self.canvas.winfo_height()))
        box_img_int = tuple(map(round, box_image))  # convert to integer or it will not work properly
        # Get scroll region box
        box_scroll = [min(box_img_int[0], box_canvas[0]), min(box_img_int[1], box_canvas[1]),
                      max(box_img_int[2], box_canvas[2]), max(box_img_int[3], box_canvas[3])]
        # Horizontal part of the image is in the visible area
        if  box_scroll[0] == box_canvas[0] and box_scroll[2] == box_canvas[2]:
            box_scroll[0]  = box_img_int[0]
            box_scroll[2]  = box_img_int[2]
        # Vertical part of the image is in the visible area
        if  box_scroll[1] == box_canvas[1] and box_scroll[3] == box_canvas[3]:
            box_scroll[1]  = box_img_int[1]
            box_scroll[3]  = box_img_int[3]
        # Convert scroll region to tuple and to integer
        self.canvas.configure(scrollregion=tuple(map(round, box_scroll)))  # set scroll region
        x1 = max(box_canvas[0] - box_image[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(box_canvas[1] - box_image[1], 0)
        x2 = min(box_canvas[2], box_image[2]) - box_image[0]
        y2 = min(box_canvas[3], box_image[3]) - box_image[1]
        if round(x2 - x1) > 0 and round(y2 - y1) > 0:  # show image if it in the visible area
            image = self.image.crop((round(x1 / self.imscale), round(y1 / self.imscale),
                                     round(x2 / self.imscale), round(y2 / self.imscale)))
            imagetk = ImageTk.PhotoImage(image.resize((round(x2 - x1), round(y2 - y1))))
            imageid = self.canvas.create_image(max(box_canvas[0], box_img_int[0]),
                                               max(box_canvas[1], box_img_int[1]),
                                               anchor='nw', image=imagetk)
            self.canvas.lower(imageid)  # set image into background
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

    def move_from(self, event):
        """ Remember previous coordinates for scrolling with the mouse """
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        """ Drag (move) canvas to the new position """
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image

    def outside(self, x, y):
        """ Checks if the point (x,y) is outside the image area """
        bbox = self.canvas.coords(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            return False  # point (x,y) is inside the image area
        else:
            return True  # point (x,y) is outside the image area

    def wheel(self, event):
        """ Zoom with mouse wheel """
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.outside(x, y): return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.im_width, self.im_height)
            if round(i * self.imscale) < 30: return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale        /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale        *= self.delta
        self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        # Redraw some figures before showing image on the screen
        self.redraw_figures()
        self.show_image()

    def redraw_figures(self):
        """ Dummy function to redraw figures in the children classes """
        pass

    def grid(self, **kw):
        """ Put CanvasImage on the parent widget """
        self.imframe.grid(**kw)  # place CanvasImage widget on the grid
        self.imframe.grid(sticky='nswe')  # make frame container sticky
        self.imframe.rowconfigure(0, weight=1)  # make canvas expandable
        self.imframe.columnconfigure(0, weight=1)

    def pack(self, **kw):
        """ Exception: cannot use pack with this widget """
        raise Exception('Cannot use pack with the widget ' + self.__class__.__name__)

    def place(self, **kw):
        """ Exceiption: cannot use place with this widget """
        raise Exception('Cannot use place with the widget ' + self.__class__.__name__)


class Polygons(CanvasImage):
    """ Class of Polygons. Inherit CanvasImage class """
    def __init__(self, parent, impath):
        ''' Initialize the Polygons '''
        CanvasImage.__init__(self, parent, impath)  # call __init__ of the CanvasImage class
        self.canvas.bind('<ButtonPress-1>', self.set_edge)  # set new edge
        self.canvas.bind('<Motion>', self.motion)  # handle mouse motion
        self.canvas.bind('<Delete>', self.delete_roi)  # delete selected polygon
        # Polygon parameters
        self.width_line = 2  # lines width
        self.dash = (1, 1)  # dash pattern
        self.color_draw = 'red'  # color to draw
        self.color_active = 'yellow'  # color of active figures
        self.color_point = 'blue'  # color of pointed figures
        self.color_back = '#808080'  # background color
        self.stipple = 'gray12'  # value of stipple
        self.tag_edge_start = '1st_edge'  # starting edge of the polygon
        self.tag_edge = 'edge'  # 2nd and subsequent edges of the polygon
        self.tag_poly = 'polygon'  # polygon tag
        self.tag_const = 'poly'  # constant tag for polygon
        self.tag_poly_line = 'poly_line'  # edge of the polygon
        self.tag_circle = 'circle'  # sticking circle tag
        self.radius_stick = 10  # distance where line sticks to the polygon's staring point
        self.radius_circle = 3  # radius of the sticking circle
        self.edge = None  # current edge of the new polygon
        self.polygon = []  # vertices of the polygon
        self.selected_poly = []  # selected polygons

    def set_edge(self, event):
        """ Set edge of the polygon """
        if self.edge and ' '.join(map(str, self.dash)) == self.canvas.itemcget(self.edge, 'dash'):
            return  # the edge is out of scope or self-crossing with other edges
        x = self.canvas.canvasx(event.x)  # get coordinates of the event on the canvas
        y = self.canvas.canvasy(event.y)
        if not self.edge:  # start drawing polygon
            self.draw_edge(x, y, (self.tag_edge_start, self.tag_edge))
            # Draw sticking circle
            self.canvas.create_oval(x - self.radius_circle, y - self.radius_circle,
                                    x + self.radius_circle, y + self.radius_circle,
                                    width=0, fill=self.color_draw,
                                    tags=(self.tag_edge, self.tag_circle))
        else:  # continue drawing polygon
            x1, y1, x2, y2 = self.canvas.coords(self.tag_edge_start)  # get coords of the 1st edge
            x3, y3, x4, y4 = self.canvas.coords(self.edge)  # get coordinates of the current edge
            if x4 == x1 and y4 == y1:  # finish drawing polygon
                if len(self.polygon) > 2:  # draw polygon on the zoomed image canvas
                    bbox = self.canvas.coords(self.container)  # get image area
                    vertices = list(map((lambda i: (i[0] * self.imscale + bbox[0],
                                                    i[1] * self.imscale + bbox[1])), self.polygon))
                    # Create identification tag
                    # [:-3] means microseconds to milliseconds, anyway there are zeros on Windows OS
                    tag_id = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')[:-3]
                    # Create polygon. 2nd tag is ALWAYS a unique tag ID + constant string.
                    self.canvas.create_polygon(vertices, fill=self.color_point,
                                               stipple=self.stipple, width=0, state='hidden',
                                               tags=(self.tag_poly, tag_id + self.tag_const))
                    # Create polyline. 2nd tag is ALWAYS a unique tag ID.
                    for j in range(len(vertices)-1):
                        self.canvas.create_line(vertices[j], vertices[j+1], width=self.width_line,
                                                fill=self.color_back, tags=(self.tag_poly_line, tag_id))
                    self.canvas.create_line(vertices[-1], vertices[0], width=self.width_line,
                                            fill=self.color_back, tags=(self.tag_poly_line, tag_id))

                self.delete_edges()  # delete edges of drawn polygon
            else:
                self.draw_edge(x, y, self.tag_edge)  # continue drawing polygon, set new edge

    def draw_edge(self, x, y, tags):
        """ Draw edge of the polygon """
        self.edge = self.canvas.create_line(x, y, x, y, fill=self.color_draw,
                                            width=self.width_line, tags=tags)
        bbox = self.canvas.coords(self.container)  # get image area
        x1 = round((x - bbox[0]) / self.imscale)  # get (x,y) on the image without zoom
        y1 = round((y - bbox[1]) / self.imscale)
        self.polygon.append((x1, y1))  # add new vertex to the list of polygon vertices

    def motion(self, event):
        """ Track mouse position over the canvas """
        if self.edge:  # relocate edge of the polygon
            x = self.canvas.canvasx(event.x)  # get coordinates of the event on the canvas
            y = self.canvas.canvasy(event.y)
            x1, y1, x2, y2 = self.canvas.coords(self.tag_edge_start)  # get coordinates of the 1st edge
            x3, y3, x4, y4 = self.canvas.coords(self.edge)  # get coordinates of the current edge
            dx = x - x1
            dy = y - y1
            # Set new coordinates of the edge
            if self.radius_stick * self.radius_stick > dx * dx + dy * dy:
                self.canvas.coords(self.edge, x3, y3, x1, y1)  # stick to the beginning
                self.canvas.itemconfigure(self.edge, dash='')  # set solid line
            else:
                self.canvas.coords(self.edge, x3, y3, x, y)  # follow the mouse movements
                if self.outside(x, y):
                    self.canvas.itemconfigure(self.edge, dash=self.dash)  # set dashed line
                else:
                    self.canvas.itemconfigure(self.edge, dash='')  # set solid line
        # Handle polygons on the canvas
        self.deselect_roi()  # change color and zeroize selected roi polygon
        self.select_roi()  # change color and select roi polygon

    def deselect_roi(self):
        """ Deselect current roi object """
        if not self.selected_poly: return  # selected polygons list is empty
        for i in self.selected_poly:
            self.canvas.itemconfigure(i, fill=self.color_back)  # deselect lines
            self.canvas.itemconfigure(i + self.tag_const, state='hidden')  # hide polygon
        self.selected_poly.clear()  # clear the list

    def select_roi(self):
        """ Select and change color of the current roi object """
        if self.edge: return  # new polygon is being created now
        i = self.canvas.find_withtag('current')  # id of the current object
        tags = self.canvas.gettags(i)  # get tags of the current object
        if self.tag_poly_line in tags:  # if it's a roi polygon. 2nd tag is ALWAYS a unique tag ID
            self.canvas.itemconfigure(tags[1], fill=self.color_point)  # select lines
            self.canvas.itemconfigure(tags[1] + self.tag_const, state='normal')  # show polygon
            self.selected_poly.append(tags[1])  # remember 2nd unique tag_id

    def redraw_figures(self):
        """ Overwritten method. Redraw sticking circle """
        bbox = self.canvas.coords(self.tag_circle)
        if bbox:  # radius of sticky circle is unchanged
            cx = (bbox[0] + bbox[2]) / 2  # center of the circle
            cy = (bbox[1] + bbox[3]) / 2
            self.canvas.coords(self.tag_circle,
                               cx - self.radius_circle, cy - self.radius_circle,
                               cx + self.radius_circle, cy + self.radius_circle)

    def delete_edges(self):
        """ Delete edges of drawn polygon """
        self.edge = None  # delete all edges and set current edge to None
        self.canvas.delete(self.tag_edge)  # delete all edges
        self.polygon.clear()  # remove all items from vertices list

    def delete_roi(self, event=None):
        """ Delete selected polygon """
        if self.edge:  # if polygon is being drawing, delete it
            self.delete_edges()  # delete edges of drawn polygon
        elif self.selected_poly:  # delete selected polygon
            for i in self.selected_poly:
                self.canvas.delete(i)  # delete lines
                self.canvas.delete(i + self.tag_const)  # delete polygon
            self.selected_poly.clear()  # clear the list


class MainWindow(ttk.Frame):
    """ Main window class """
    def __init__(self, mainframe, path):
        """ Initialize the main Frame """
        ttk.Frame.__init__(self, master=mainframe)
        self.master.title('Draw polygons')
        self.master.geometry('800x600')
        self.master.rowconfigure(0, weight=1)  # make the CanvasImage expandable
        self.master.columnconfigure(0, weight=1)
        polygons = Polygons(self.master, path)
        polygons.grid(row=0, column=0)


filename = './Data/doge.jpg'  # place path to your image here
root = tk.Tk()
app = MainWindow(root, path=filename)
root.mainloop()
