# -*- coding: utf-8 -*-
# WARNING: This is a simplified zoom example.
# You should use more advanced techniques to not cram the memory
# with a huge resized image for the large zooms.
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class AutoScrollbar(ttk.Scrollbar):
    ''' A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager '''
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
        ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')

class Zoom(ttk.Frame):
    ''' Simple zoom with mouse wheel '''
    def __init__(self, mainframe, path):
        ''' Initialize the main Frame '''
        ttk.Frame.__init__(self, master=mainframe)
        self.master.title('Simple zoom with mouse wheel')
        # Vertical and horizontal scrollbars for canvas
        vbar = AutoScrollbar(self.master, orient='vertical')
        hbar = AutoScrollbar(self.master, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')
        # Open image
        self.image = Image.open(path)
        # Create canvas and put image on it
        self.canvas = tk.Canvas(self.master, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        vbar.configure(command=self.canvas.yview)  # bind scrollbars to the canvas
        hbar.configure(command=self.canvas.xview)
        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.canvas.bind('<ButtonPress-1>', self.move_from)
        self.canvas.bind('<ButtonPress-3>', self.get_coords)  # get coords of the image
        self.canvas.bind('<B1-Motion>',     self.move_to)
        self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',   self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>',   self.wheel)  # only with Linux, wheel scroll up
        # Show image and plot some random test rectangles on the canvas
        self.imscale = 1.0
        self.imageid = None
        self.delta = 0.75
        width, height = self.image.size
        minsize, maxsize = 5, 20
        for n in range(10):
            x0 = random.randint(0, width - maxsize)
            y0 = random.randint(0, height - maxsize)
            x1 = x0 + random.randint(minsize, maxsize)
            y1 = y0 + random.randint(minsize, maxsize)
            color = ('red', 'orange', 'yellow', 'green', 'blue')[random.randint(0, 4)]
            self.canvas.create_rectangle(x0, y0, x1, y1, outline='black', fill=color,
                                         activefill='black', tags=n)
        # Text is used to set proper coordinates to the image. You can make it invisible.
        self.text = self.canvas.create_text(0, 0, anchor='nw', text='Scroll to zoom')
        self.show_image()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def get_coords(self, event):
        """ Get coordinates of the mouse click event on the image """
        x1 = self.canvas.canvasx(event.x)  # get coordinates of the event on the canvas
        y1 = self.canvas.canvasy(event.y)
        xy = self.canvas.coords(self.imageid)  # get coords of image's upper left corner
        x2 = round((x1 - xy[0]) / self.imscale)  # get real (x,y) on the image without zoom
        y2 = round((y1 - xy[1]) / self.imscale)
        if 0 <= x2 <= self.image.size[0] and 0 <= y2 <= self.image.size[1]:
            print(x2, y2)
        else:
            print('Outside of the image')

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:
            scale        *= self.delta
            self.imscale *= self.delta
        if event.num == 4 or event.delta == 120:
            scale        /= self.delta
            self.imscale /= self.delta
        # Rescale all canvas objects
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.canvas.scale('all', x, y, scale, scale)
        self.show_image()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def show_image(self):
        ''' Show image on the Canvas '''
        if self.imageid:
            self.canvas.delete(self.imageid)
            self.imageid = None
            self.canvas.imagetk = None  # delete previous image from the canvas
        width, height = self.image.size
        new_size = int(self.imscale * width), int(self.imscale * height)
        imagetk = ImageTk.PhotoImage(self.image.resize(new_size))
        # Use self.text object to set proper coordinates
        self.imageid = self.canvas.create_image(self.canvas.coords(self.text),
                                                anchor='nw', image=imagetk)
        self.canvas.lower(self.imageid)  # set it into background
        self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

path = './data-2/doge.jpg'  # place path to your image here
root = tk.Tk()
app = Zoom(root, path=path)
root.mainloop()
