# -*- coding: utf-8 -*-
import tkinter as tk

from tkinter import ttk
from PIL import Image, ImageTk
from logic_logger import logging
from gui_autoscrollbar import AutoScrollbar

class ImageFrame():
    """ Display an image and necessary functional for flight mission formation """
    def __init__(self, parent, placeholder, path, roi_size):
        """ Initialize the ImageFrame """
        self.cancelled = False  # image initialization is cancelled by the user
        self.__parent = parent  # flight task object that calls this ImageFrame class
        Locale.__init__(self)
        self.set_locale(self.__parent.locale)  # set interface language
        self.path = path  # path to the image, should be public
        self.classname = None  # class name of the underlying surface, should be public
        self.__roi_size = roi_size  # obtain size of the roi
        self.__roi_tag = 'roi'
        self.__imscale = 1.0  # scale for the canvas image zoom
        self.__delta = 1.3  # zoom magnitude
        self.__warning1 = self._('Too close to the edge')
        self.__warning2 = self._('Select object class')
        self.__text_size = 14  # size of the text
        self.__font = 'Helvetica {size} normal'
        self.__font_max_size = 20  # max font size
        self.__font_min_size = 7  # min font size
        self.__text_tag = 'text'
        # Create ImageFrame in parent widget and make it expandable
        self.__imframe = ttk.Frame(placeholder)  # placeholder of the ImageFrame objects
        self.__imframe.grid(row=0, column=0, sticky='nswe')
        self.__imframe.rowconfigure(0, weight=1)  # make it expandable
        self.__imframe.columnconfigure(0, weight=1)
        # Vertical and horizontal scrollbars for canvas
        hbar = AutoScrollbar(self.__imframe, orient='horizontal')
        vbar = AutoScrollbar(self.__imframe, orient='vertical')
        hbar.grid(row=1, column=0, sticky='we')
        vbar.grid(row=0, column=1, sticky='ns')
        # Create canvas and bind it with scrollbars
        self.__canvas = tk.Canvas(self.__imframe, highlightthickness=0,
                                  xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.__canvas.grid(row=0, column=0, sticky='nswe')
        self.__canvas.update()  # wait till canvas is created
        hbar.configure(command=self.__scroll_x)  # bind scrollbars to the canvas
        vbar.configure(command=self.__scroll_y)
        # Create a popup menu for ImageFrame
        self.hold_focus = False  # hold focus when popup is opened
        self.__hold_selection = False  # hold selection when popup menu is opened
        self.__selected_text = []
        self.__label_delete = self._('Delete')
        self.__previous_state = 0  # previous state of the event
        self.__menu = tk.Menu(self.__canvas, tearoff=0)
        self.__menu.add_command(label       = self.__label_delete,
                                command     = self.delete_roi,
                                accelerator = 'Delete')
        # Bind events to the Canvas
        self.__canvas.bind('<Configure>', self.__show_image)  # canvas is resized
        self.__canvas.bind('<ButtonPress-1>', self.__set_roi)  # set roi image
        self.__canvas.bind('<ButtonPress-3>', self.__move_from)
        self.__canvas.bind('<ButtonRelease-3>', self.__popup)  # call popup menu
        self.__canvas.bind('<B3-Motion>', self.__move_to)  # move canvas with right mouse button
        self.__canvas.bind('<Motion>', self.__motion)  # handle mouse motion
        self.__canvas.bind('<MouseWheel>', self.__wheel)  # with Windows and MacOS, but not Linux
        self.__canvas.bind('<Button-5>', self.__wheel)  # only with Linux, wheel scroll down
        self.__canvas.bind('<Button-4>', self.__wheel)  # only with Linux, wheel scroll up
        self.__canvas.bind('<Delete>', self.delete_roi)  # delete selected roi image
        self.__canvas.bind('<Leave>', self.__rid_focus)  # hide roi and remove focus from the canvas
        self.__canvas.bind('<Enter>', self.__set_focus)  # set focus on the canvas
        # Handle keystrokes in idle mode, because program slows down on a weak computers,
        # when too many key stroke events in the same time
        self.__canvas.bind('<Key>', lambda event: self.__canvas.after_idle(self.__keystroke, event))
        logging.info('Open image: {}'.format(self.path))
        with warnings.catch_warnings():  # suppress DecompressionBombWarning for the huge image
            warnings.simplefilter('ignore')
            self.__image = Image.open(self.path)  # open image
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.__container = self.__canvas.create_rectangle((0, 0, self.__image.size), width=0)
        # Set region of interest (roi) rectangle on the canvas and make it invisible
        self.__roi_rect = self.__canvas.create_rectangle((0, 0, 0, 0), width=2, outline='red',
                                                         state='hidden')
        # Set text-classname on the canvas and make it invisible
        self.__text = self.__canvas.create_text((0, 0), anchor='sw', fill='red',
            state='hidden', font=self.__font.format(size=self.__text_size), tag=self.__text_tag)
        # Set text-warning on the canvas and make it invisible. Text-classname and text-warning are
        # different, because text-classname lifts every time, but warning stay beneath the drawing.
        # This is necessary for popup menu. It'll not show if warning above the drawing.
        self.__text_warning = self.__canvas.create_text((0, 0), anchor='sw', fill='red',
            state='hidden', font=self.__font.format(size=self.__text_size), tag=self.__text_tag)
        #
        # Decide if this is a huge image or not
        self.__w, self.__h = self.__image.size  # image width and height
        self.__min_side = min(self.__w, self.__h)  # get the smaller image side
        self.__max_side = max(self.__w, self.__h)  # get the bigger image side
        self.__filter = Image.ANTIALIAS  # could be: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
        self.__is_huge = False  # huge image or not
        self.__is_tiny = False  # is it tiny copy of the image or not
        self.__smaller_image = None  # smaller image from the huge image
        self.__tiny_image = None  # tiny image from the smaller image
        self.__huge_size = 14000  # define size of the huge image
        self.__tiny_size = 3072  # define size of the tiny image
        if self.__w * self.__h > self.__huge_size * self.__huge_size:
            self.__is_huge = True  # image is huge
            if self.__image.tile[0][0] != 'raw':  # only raw / uncompressed images could be tiled
                warnings.warn('Only "raw" images could be tiled')  # show warning
            self.__offset = self.__image.tile[0][2]  # initial tile offset
            self.__tile = [
                self.__image.tile[0][0],  # image should be 'raw' or uncompressed
                [0, 0, self.__w, self.__canvas.winfo_height()],  # tile rectangle
                self.__offset,
                self.__image.tile[0][3]]  # list of arguments to the decoder
            self.__smaller_image = self.__resize1()  # create smaller image
            if self.cancelled: return  # exit from init and close ImageFrame in the main GUI
        #
        if self.__w * self.__h > self.__tiny_size * self.__tiny_size:
            self.__is_tiny = True  # create tiny copy of the larger image
            if self.__is_huge:  # make tiny copy from the smaller image
                self.__tiny_image = self.__resize2(self.__smaller_image, self.__tiny_size)
            else:  # make tiny copy from the original image
                self.__tiny_image = self.__resize2(self.__image, self.__tiny_size)
            # Create MD5 hash sum from the tiny image
            md5 = hashlib.md5(self.__tiny_image.tobytes())  # MD5 from tiny image
            md5.update(b'This is a tiny copy of the big image')  # try to make MD5 unique with this string
            self.__md5 = md5.hexdigest()  # get MD5 hash in hex format
        else:  # original image is tiny, so get MD5 hash from original image
            self.__md5 = hashlib.md5(self.__image.tobytes()).hexdigest()
        #
        self.__show_image()  # zoom tile and show it on the canvas
        self.__get_data()  # fill ImageFrame with roi images
        #
        x, y = self.__canvas.winfo_pointerxy()  # get mouse position
        i, j = self.__canvas.winfo_rootx(), self.__canvas.winfo_rooty()  # get canvas position
        w, h = self.__canvas.winfo_width(), self.__canvas.winfo_height()  # get canvas size
        if i <= x < i+w and j <= y < j+h:
            self.__canvas.event_generate('<Enter>', x=x-i, y=y-j)  # set focus on the canvas
        else:
            self.__imframe.after_idle(self.__parent.set_focus)  # set focus on the tree

    def __resize1(self):
        """ Resize image proportionally without loading it to RAM and create smaller image """
        w1, h1 = float(self.__w), float(self.__h)
        w2, h2 = float(self.__huge_size), float(self.__huge_size)
        aspect_ratio1 = w1 / h1
        aspect_ratio2 = w2 / h2  # == 1
        #
        if aspect_ratio1 == aspect_ratio2:
            image = Image.new('RGB', (int(w2), int(h2)))
            k = h2 / h1  # compression ratio
            w = int(w2)  # band length
        elif aspect_ratio1 > aspect_ratio2:
            image = Image.new('RGB', (int(w2), int(w2 / aspect_ratio1)))
            k = h2 / w1  # compression ratio
            w = int(w2)  # band length
        else:  # aspect_ratio1 < aspect_ration2
            image = Image.new('RGB', (int(h2 * aspect_ratio1), int(h2)))
            k = h2 / h1 # compression ratio
            w = int(h2 * aspect_ratio1)  # band length
        #
        r = Resize(self.__parent.parent, image, self.path, k, w)  # resize image
        self.__parent.parent.wait_window(r)  # display the modal dialog and wait for it to close
        self.cancelled = image.cancelled
        return image

    def __resize2(self, image, size):
        """ Resize image proportionally """
        w1, h1 = image.size
        w1, h1 = float(w1), float(h1)
        w2, h2 = float(size), float(size)
        aspect_ratio1 = w1 / h1
        aspect_ratio2 = w2 / h2
        if aspect_ratio1 == aspect_ratio2:
            return image.resize((int(w2), int(h2)), self.__filter)
        elif aspect_ratio1 > aspect_ratio2:
            return image.resize((int(w2), int(w2 / aspect_ratio1)), self.__filter)
        else:  # aspect_ratio1 < aspect_ratio2
            return image.resize((int(h2 * aspect_ratio1), int(h2)), self.__filter)

    def __get_data(self):
        """ Get data about selected roi images on this ImageFrame picture from the parent object """
        l = self.__parent.get_data(self.__md5)  # get list of tuples (x, y, classname, image_name)
        for x, y, classname, imname in l:
            bbox = (x, y, x + self.__roi_size[0], y + self.__roi_size[1])
            self.__draw_roi(bbox, classname, imname)

    def __get_roi(self):
        """ Obtain roi image rectangle and send it to the parent object.
            Return upper left corner coordinates (x,y) of the roi rectangle on the image. """
        if self.__canvas.itemcget(self.__roi_rect, 'state') == 'hidden':  # roi is hidden
            x, y, roi = None, None, None
        else:
            bbox1 = self.__canvas.coords(self.__container)  # get image area
            bbox2 = self.__canvas.coords(self.__roi_rect)  # get roi area
            x = int((bbox2[0] - bbox1[0]) / self.__imscale)  # get (x,y) on the image
            y = int((bbox2[1] - bbox1[1]) / self.__imscale)
            if self.__is_huge:  # image is huge
                self.__tile[1][3] = self.__roi_size[1]  # set the tile height
                self.__tile[2] = self.__offset + self.__w * y * 3  # set offset of the band
                self.__image = Image.open(self.path)  # open image
                self.__image.size = (self.__w, self.__roi_size[1])  # set size of the tile band
                self.__image.tile = [self.__tile]
                roi = self.__image.crop((x, 0, x + self.__roi_size[0], self.__roi_size[1]))
            else:  # image is normal and totally in RAM
                roi = self.__image.crop((x, y, x + self.__roi_size[0],
                            y + self.__roi_size[1]))  # cut sub-rectangle from the image
        self.__parent.show_roi(roi)  # parent object must have 'show_roi' method
        return x, y  # roi coords (x,y) on the image

    def __set_roi(self, event):
        """ Obtain roi image rectangle and save it to the parent object.
            Also mark and remember position of selected area on the main image """
        x, y = self.__get_roi()  # get upper left corner coords of the roi on the image
        if x:  # if not None, draw gray rectangle and save it's position on the image
            bbox = self.__canvas.coords(self.__roi_rect)  # get roi area
            # [:-3] means microseconds to milliseconds, anyway there are zeros on Windows OS
            dt = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')[:-3]
            imname = self.classname + '.' + dt + '.png'
            self.__draw_roi(bbox, self.classname, imname)
            self.__parent.save_roi(x, y, self.__md5, imname)  # parent must have 'save_roi'

    def set_roi_size(self, roi_size):
        """ Set new value for roi_size and zeroize classname """
        self.__roi_size = roi_size  # set new size
        self.classname = None  # zeroize class name

    def __draw_roi(self, bbox, classname, imname):
        """ Draw roi rectangle and text with the class name for it """
        # Text is 1st, rect is 2nd. It is necessary for __select_roi method.
        # Tags for text: 1st = roi_tag; 2nd = text_tag; 3rd = image_name.
        # Tags orther for text is necessary for __delete method.
        size = min(self.__font_max_size, max(self.__font_min_size,  # configure font size
                                             int(self.__text_size * self.__imscale)))
        self.__canvas.create_text((bbox[0], bbox[1]), text=classname, anchor='sw', fill='gray',
                                  tags=(self.__roi_tag, self.__text_tag, imname, classname),
                                  font=self.__font.format(size=size))
        self.__canvas.create_rectangle(bbox, width=2, outline='gray', tag=self.__roi_tag)

    def __move_from(self, event):
        """ Remember previous coordinates for scrolling with the mouse """
        self.__canvas.scan_mark(event.x, event.y)

    def __move_to(self, event):
        """ Drag (move) canvas to the new position """
        self.__canvas.scan_dragto(event.x, event.y, gain=1)
        self.__show_image()  # zoom tile and show it on the canvas

    def __motion(self, event):
        """ Track mouse position over the canvas """
        if self.hold_focus or self.__parent.hold_focus: return
        x = self.__canvas.canvasx(event.x)  # get coordinates of the event on the canvas
        y = self.__canvas.canvasy(event.y)
        w = (self.__roi_size[0] * self.__imscale) / 2
        h = (self.__roi_size[1] * self.__imscale) / 2
        bbox = self.__canvas.coords(self.__container)  # get image area
        # Check if class name of the underlying surface is set
        if not self.classname:  # show warning 2
            self.__canvas.coords(self.__text_warning, (x, y))
            self.__canvas.itemconfigure(self.__text_warning, text=self.__warning2, state='normal')
            self.__canvas.itemconfigure(self.__text, state='hidden')  # hide class name
            self.__canvas.itemconfigure(self.__roi_rect, state='hidden')  # hide roi
        # Draw roi rectangle
        elif bbox[0] + w <= x < bbox[2] - w and bbox[1] + h <= y < bbox[3] - h:
            self.__canvas.coords(self.__text, (x-w, y-h))  # relocate class name
            self.__canvas.coords(self.__roi_rect, (x - w, y - h, x + w, y + h))  # relocate roi
            self.__canvas.itemconfigure(self.__text, text=self.classname, state='normal')
            self.__canvas.itemconfigure(self.__roi_rect, state='normal')  # show roi
            self.__canvas.lift(self.__roi_rect)  # set roi into foreground
            self.__canvas.lift(self.__text)  # set text into foreground
            self.__canvas.itemconfigure(self.__text_warning, state='hidden')  # hide warning
        else:  # otherwise show warning 1
            self.__canvas.coords(self.__text_warning, (x, y))
            self.__canvas.itemconfigure(self.__text_warning, text=self.__warning1, state='normal')
            self.__canvas.itemconfigure(self.__text, state='hidden')
            self.__canvas.itemconfigure(self.__roi_rect, state='hidden')  # hide roi
        self.__get_roi()  # update preview image in the ImageList class
        # Handle roi images on the canvas
        self.deselect_roi()  # change color and zeroize selected roi text and rect
        current_id = self.__canvas.find_withtag('current')  # id of the current object
        self.__selected_text = self.__select_roi(current_id)

    def __select_roi(self, id):
        """ Select and change color of the current roi object """
        tags = self.__canvas.gettags(id)  # get tags of the current object
        selected_text = []
        if self.__roi_tag in tags:  # if it's a roi image (text or rectangle)
            if self.__text_tag in tags:  # if it's a text
                selected_text = [id[0]]
            else:  # if it's a rectangle
                selected_text = [id[0]-1]  # text is 1st, rect is 2nd
            # There is only 1 roi object, so no need for cycle. Text is 1st, rect is 2nd
            self.__canvas.itemconfigure(selected_text[0], fill='yellow')
            self.__canvas.itemconfigure(selected_text[0]+1, outline='yellow')
        return selected_text

    def select_roi(self, name):
        """ Try to find and select roi object or class objects outside of the ImageFrame """
        self.deselect_roi()  # drop previous selection
        ids = self.__canvas.find_withtag(name)  # try to get ids of the roi or class
        for id in ids:
            self.__selected_text.append(id)  # text is 1st, rect is 2nd
            self.__canvas.itemconfigure(id, fill='yellow')
            self.__canvas.itemconfigure(id+1, outline='yellow')

    def deselect_roi(self):
        """ Deselect current roi object (text and rectangle) or class objects """
        for id in self.__selected_text:
            self.__canvas.itemconfigure(id, fill='gray')  # text is 1st, rect is 2nd
            self.__canvas.itemconfigure(id+1, outline='gray')
        self.__selected_text = []

    def __wheel(self, event):
        """ Zoom with mouse wheel """
        x = self.__canvas.canvasx(event.x)  # get coordinates of the event on the canvas
        y = self.__canvas.canvasy(event.y)
        bbox = self.__canvas.coords(self.__container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        else: return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            if int(self.__min_side * self.__imscale) < 30: return  # image is less than 30 pixels
            self.__imscale /= self.__delta
            scale          /= self.__delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.__canvas.winfo_width(), self.__canvas.winfo_height())
            if i < self.__imscale: return  # 1 pixel is bigger than the visible area
            self.__imscale *= self.__delta
            scale          *= self.__delta
        self.__canvas.scale('all', x, y, scale, scale)  # rescale all objects
        size = min(self.__font_max_size, max(self.__font_min_size,  # configure font size
                                             int(self.__text_size * self.__imscale)))
        self.__canvas.itemconfigure(self.__text_tag, font=self.__font.format(size=size))
        self.__show_image()  # zoom tile and show it on the canvas

    def __popup(self, event):
        """ Popup menu """
        self.__motion(event)  # select roi with popup menu explicitly to be sure it is selected
        if self.__selected_text:  # show popup menu only for selected text and rectangle
            self.hold_focus = True  # popup menu is opened
            self.__hold_selection = True  # hold selection when popup menu is opened
            self.__rid_focus()  # delete roi rectangle
            self.__menu.post(event.x_root, event.y_root)  # show popup menu
            self.__set_focus(event)  # set focus on the canvas
            self.hold_focus = False  # popup menu is closed

    def delete_roi(self, event=None):
        """ Delete selected roi object or class objects """
        for id in self.__selected_text:
            imname = self.__canvas.gettags(id)[2]  # image_name tag is the 3rd
            imname = unicode(imname, 'utf-8')  # tags somehow are saved in ASCII format
            self.__canvas.delete(id)  # delete text from the canvas
            self.__canvas.delete(id+1)  # delete rectangle from the canvas
            self.__parent.delete(imname)  # delete image from the parent object
        self.__selected_text = []

    def __set_focus(self, event):
        """ Set focus on the canvas and handle <Alt>+<Tab> switches between windows """
        self.__canvas.focus_set()
        if self.hold_focus or self.__parent.hold_focus: return
        if self.__hold_selection:  # hold selection only one time
            self.__hold_selection = False
            return
        self.__parent.deselect()  # remove selection in the ImageList widget
        self.__motion(event)

    def __rid_focus(self, event=None):
        """ Hide region of interest and remove focus from the canvas """
        self.__canvas.itemconfigure(self.__text, state='hidden')  # hide text
        self.__canvas.itemconfigure(self.__text_warning, state='hidden')  # hide warning
        self.__canvas.itemconfigure(self.__roi_rect, state='hidden')  # hide roi
        if self.hold_focus or self.__parent.hold_focus or self.__hold_selection: return
        self.deselect_roi()  # drop selection of the roi image
        self.__get_roi()  # remove preview image in the ImageList class
        self.__imframe.focus_set()  # remove focus from the canvas by setting it elsewhere

    def __keystroke(self, event):
        """ Scrolling with the keyboard, like a gamer.
            Independent from the language of the keyboard, CapsLock, <Ctrl>+<key>, etc. """
        if event.state - self.__previous_state == 4:  # means that the Control key is pressed
            pass  # do nothing
        else:
            self.__previous_state = event.state  # remember the last keystroke state
            # Up, Down, Left, Right keystrokes
            if event.keycode in [68, 39, 102]:  # scroll right, keys 'd' or 'Right'
                self.__scroll_x('scroll',  1, 'unit', event=event)
            elif event.keycode in [65, 37, 100]:  # scroll left, keys 'a' or 'Left'
                self.__scroll_x('scroll', -1, 'unit', event=event)
            elif event.keycode in [87, 38, 104]:  # scroll up, keys 'w' or 'Up'
                self.__scroll_y('scroll', -1, 'unit', event=event)
            elif event.keycode in [83, 40, 98]:  # scroll down, keys 's' or 'Down'
                self.__scroll_y('scroll',  1, 'unit', event=event)

    def __scroll_x(self, *args, **kwargs):
        """ Scroll canvas horizontally and redraw the image """
        self.__canvas.xview(*args)  # scroll horizontally
        self.__show_image()  # redraw the tile
        if kwargs and kwargs['event']:
            self.__motion(kwargs['event'])

    def __scroll_y(self, *args, **kwargs):
        """ Scroll canvas vertically and redraw the image """
        self.__canvas.yview(*args)  # scroll vertically
        self.__show_image()  # redraw the tile
        if kwargs and kwargs['event']:
            self.__motion(kwargs['event'])

    def __show_image(self, event=None):
        """ Show image on the Canvas. Implements correct image zoom like in Google Maps """
        box_image = self.__canvas.coords(self.__container)  # get image area
        box_canvas = (self.__canvas.canvasx(0),  # get visible area of the canvas
                      self.__canvas.canvasy(0),
                      self.__canvas.canvasx(self.__canvas.winfo_width()),
                      self.__canvas.canvasy(self.__canvas.winfo_height()))
        box_img_int = tuple(map(int, box_image))  # convert to integer or it will not work properly
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
        self.__canvas.configure(scrollregion=tuple(map(int, box_scroll)))  # set scroll region
        x1 = max(box_canvas[0] - box_image[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(box_canvas[1] - box_image[1], 0)
        x2 = min(box_canvas[2], box_image[2]) - box_image[0]
        y2 = min(box_canvas[3], box_image[3]) - box_image[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            size = self.__max_side * self.__imscale  # current size of the image
            if self.__is_tiny and size < self.__tiny_size:
                # Replace original image with the tiny image
                imscale = size / self.__tiny_size
                image = self.__tiny_image.crop((int(x1 / imscale), int(y1 / imscale),
                                                int(x2 / imscale), int(y2 / imscale)))
            elif self.__is_huge and size < self.__huge_size:
                # Replace original image with the smaller image
                imscale = size / self.__huge_size
                image = self.__smaller_image.crop((int(x1 / imscale), int(y1 / imscale),
                                                   int(x2 / imscale), int(y2 / imscale)))
            elif self.__is_huge:  # open huge image
                # Use tile band to crop tile from the original huge image
                h = int((y2 - y1) / self.__imscale)  # height of the tile band
                self.__tile[1][3] = h  # set the tile height
                self.__tile[2] = self.__offset + self.__w * int(y1 / self.__imscale) * 3
                self.__image = Image.open(self.path)  # open image
                self.__image.size = (self.__w, h)  # set size of the tile band
                self.__image.tile = [self.__tile]
                image = self.__image.crop((int(x1 / self.__imscale), 0,
                                           int(x2 / self.__imscale), h))
            else:  # open normal image
                image = self.__image.crop((int(x1 / self.__imscale), int(y1 / self.__imscale),
                                           int(x2 / self.__imscale), int(y2 / self.__imscale)))
            #
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1)), self.__filter))
            imageid = self.__canvas.create_image(max(box_canvas[0], box_img_int[0]),
                                                 max(box_canvas[1], box_img_int[1]),
                                                 anchor='nw', image=imagetk)
            self.__canvas.lower(imageid)  # set image into background
            self.__canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

    def destroy(self):
        """ ImageFrame destructor """
        logging.info('Close image: {}'.format(self.path))
        if self.__smaller_image: self.__smaller_image.close()
        if self.__tiny_image: self.__tiny_image.close()
        self.__image.close()
        self.__canvas.destroy()
        self.__imframe.destroy()
