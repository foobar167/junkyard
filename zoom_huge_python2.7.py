# -*- coding: utf-8 -*-
# Open and zoom huge images upto several Gigabytes and more.
# Only 'raw' (uncompressed) formats could be opened for huge files.
# It zooms only a tile, but not the whole image. So the zoomed tile occupies
# constant memory and not crams it with a huge resized image for the large zooms.
import warnings
import ttk
import Tkinter as tk
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
        raise tk.TclError(u'Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError(u'Cannot use place with this widget')

class Zoom_Advanced(ttk.Frame):
    ''' Advanced zoom of the image '''
    def __init__(self, mainframe, path):
        ''' Initialize the main Frame '''
        ttk.Frame.__init__(self, master=mainframe)
        self.master.title(u'Zoom with mouse wheel')
        self.master.geometry(u'800x600')
        # Vertical and horizontal scrollbars for canvas
        vbar = AutoScrollbar(self.master, orient=u'vertical')
        hbar = AutoScrollbar(self.master, orient=u'horizontal')
        vbar.grid(row=0, column=1, sticky=u'ns')
        hbar.grid(row=1, column=0, sticky=u'we')
        # Create canvas and put image on it
        self.canvas = tk.Canvas(self.master, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky=u'nswe')
        self.canvas.update()  # wait till canvas is created
        self.canvas.focus_set()  # set focus on the canvas
        vbar.configure(command=self.scroll_y)  # bind scrollbars to the canvas
        hbar.configure(command=self.scroll_x)
        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.canvas.bind(u'<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind(u'<ButtonPress-1>', self.move_from)
        self.canvas.bind(u'<B1-Motion>',     self.move_to)
        self.canvas.bind(u'<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind(u'<Button-5>',   self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind(u'<Button-4>',   self.wheel)  # only with Linux, wheel scroll up
        with warnings.catch_warnings():  # suppress DecompressionBombWarning for the huge image
            warnings.simplefilter(u'ignore')
            self.image = Image.open(path)  # open image
        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)
        # Decide if this is a huge image or not
        self.huge_image = False  # huge image or not
        self.smaller_image = None  # smaller image from huge image
        self.huge_size = 14000  # define size of the huge image
        self.tiny_size = 2048  # define size of the tiny image
        if self.width * self.height > self.huge_size * self.huge_size:
            self.huge_image = True  # image is huge
            if self.image.tile[0][0] != u'raw':  # only raw images could be tiled
                warnings.warn(u'Only "raw" images could be tiled')  # show warning for not raw images
            self.offset = self.image.tile[0][2]  # initial tile offset
            self.tile = [self.image.tile[0][0],  # it should be 'raw'
                         [0, 0, self.width, self.master.winfo_height()],  # tile extent (a rectangle)
                         self.offset,
                         self.image.tile[0][3]]  # list of arguments to the decoder
            self.size = max(self.width, self.height)  # get the bigger image side
            self.smaller_image = self.resize1()  # create smaller image
            self.tiny_image = self.resize2(self.smaller_image, self.tiny_size)  # create tiny image
        self.show_image()

    def resize1(self):
        ''' Resize image proportionally and create smaller image '''
        w1, h1 = float(self.width), float(self.height)
        w2, h2 = float(self.huge_size), float(self.huge_size)
        aspect_ratio1 = w1 / h1
        aspect_ratio2 = w2 / h2  # == 1
        i = 0
        if aspect_ratio1 == aspect_ratio2:
            image = Image.new(u'RGB', (int(w2), int(h2)))
            k = h2 / h1  # compression ratio
            w = int(w2)  # band length
        elif aspect_ratio1 > aspect_ratio2:
            image = Image.new(u'RGB', (int(w2), int(w2 / aspect_ratio1)))
            k = h2 / w1  # compression ratio
            w = int(w2)  # band length
        else:  # aspect_ratio1 < aspect_ration2
            image = Image.new(u'RGB', (int(h2 * aspect_ratio1), int(h2)))
            k = h2 / h1 # compression ratio
            w = int(h2 * aspect_ratio1)  # band length
        while i < self.height:
            band_width = min(1024, self.height - i)  # width of the tile band
            self.tile[1][3] = band_width  # set band width
            self.tile[2] = self.offset + self.width * i * 3  # set tile offset
            self.image = Image.open(path)  # open image
            self.image.size = (self.width, band_width)  # set size of the tile band
            self.image.tile = [self.tile]  # set tile
            band = self.image.crop((0, 0, self.width, band_width))  # crop tile band
            image.paste(band.resize((w, int(band_width * k)+1), Image.NEAREST), (0, int(i * k)))
            i += band_width
        return image

    def resize2(self, image, size):
        ''' Resize image proportionally and create smaller image '''
        w1, h1 = image.size
        w1, h1 = float(w1), float(h1)
        w2, h2 = float(size), float(size)
        aspect_ratio1 = w1 / h1
        aspect_ratio2 = w2 / h2
        if aspect_ratio1 == aspect_ratio2:
            return image.resize((int(w2), int(h2)), Image.NEAREST)
        elif aspect_ratio1 > aspect_ratio2:
            return image.resize((int(w2), int(w2 / aspect_ratio1)), Image.NEAREST)
        else:  # aspect_ratio1 < aspect_ratio2
            return image.resize((int(h2 * aspect_ratio1), int(h2)), Image.NEAREST)

    def scroll_y(self, *args):
        ''' Scroll canvas vertically and redraw the image '''
        self.canvas.yview(*args)  # scroll vertically
        self.show_image()  # redraw the image

    def scroll_x(self, *args):
        ''' Scroll canvas horizontally and redraw the image '''
        self.canvas.xview(*args)  # scroll horizontally
        self.show_image()  # redraw the image

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = self.canvas.coords(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        else: return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30: return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale        /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale        *= self.delta
        self.canvas.scale(u'all', x, y, scale, scale)  # rescale all canvas objects
        self.show_image()

    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        bbox1 = self.canvas.coords(self.container)  # get image area
        # Make bbox1 an integer, otherwise scroll region doesn't work properly
        bbox1 = tuple(map(int, bbox1))
        bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if  bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0]  = bbox1[0]
            bbox[2]  = bbox1[2]
        if  bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1]  = bbox1[1]
            bbox[3]  = bbox1[3]
        self.canvas.configure(scrollregion=tuple(bbox))  # set scroll region
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area

            if self.huge_image:  # open huge image
                if self.size * self.imscale < self.tiny_size:
                    # Replace original image with the tiny image
                    imscale = self.imscale * self.size / self.tiny_size
                    x = min(int(x2 / imscale), self.tiny_image.size[0])  # sometimes it is larger on 1 pixel...
                    y = min(int(y2 / imscale), self.tiny_image.size[1])  # ...and sometimes not
                    image = self.tiny_image.crop((int(x1 / imscale),
                                                  int(y1 / imscale), x, y))
                elif self.size * self.imscale < self.huge_size:
                    # Replace original image with the smaller image
                    imscale = self.imscale * self.size / self.huge_size
                    x = min(int(x2 / imscale), self.smaller_image.size[0])  # sometimes it is larger on 1 pixel...
                    y = min(int(y2 / imscale), self.smaller_image.size[1])  # ...and sometimes not
                    image = self.smaller_image.crop((int(x1 / imscale),
                                                     int(y1 / imscale), x, y))
                else:  # use tile band to crop tile from the original image
                    h = int((y2 - y1) / self.imscale)  # height of the tile band
                    self.tile[1][3] = h  # set the tile height
                    self.tile[2] = self.offset + self.width * int(y1 / self.imscale) * 3
                    self.image = Image.open(path)  # open image
                    self.image.size = (self.width, h)  # set size of the tile band
                    self.image.tile = [self.tile]
                    x = min(int(x2 / self.imscale), self.width)  # sometimes it is larger on 1 pixel...
                    image = self.image.crop((int(x1 / self.imscale), 0, x, h))
            else:  # open normal image
                x = min(int(x2 / self.imscale), self.width)  # sometimes it is larger on 1 pixel...
                y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not
                image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))

            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                               anchor=u'nw', image=imagetk)
            self.canvas.lower(imageid)  # set image into background
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

#path = u'doge.jpg'  # place path to your image here
#path = u'd:/Data/TechnologySG_2016_Datasets/Airbases_Segmentation/rect1_minsk1/z18/yandex_z18_1-1.tif'
path = u'd:/Temp/horizontal.tif'
root = tk.Tk()
app = Zoom_Advanced(root, path=path)
root.mainloop()
