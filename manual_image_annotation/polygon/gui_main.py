# -*- coding: utf-8 -*-
import os
import tkinter as tk

from PIL import Image
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from .gui_imageframe import ImageFrame
from .logic_config import Config
from .logic_logger import logging, handle_exception

class MainGUI(ttk.Frame):
    """ GUI of Image Viewer """
    def __init__(self, mainframe):
        """ Initialize the Frame """
        logging.info('Open GUI')
        ttk.Frame.__init__(self, master=mainframe)
        self.__create_instances()
        self.__create_main_window()
        self.__create_widgets()

    def __create_instances(self):
        """ Instances for GUI are created here """
        self.__config = Config()  # open config file of the main window
        self.__imframe = None  # empty instance of image frame (canvas)

    def __create_main_window(self):
        """ Create main window GUI"""
        self.__default_title = 'Image Viewer'
        self.master.title(self.__default_title)
        self.master.geometry(self.__config.get_win_geometry())  # get window size/position from config
        self.master.wm_state(self.__config.get_win_state())  # get window state
        # self.destructor gets fired when the window is destroyed
        self.master.protocol('WM_DELETE_WINDOW', self.destroy)
        #
        self.__menubar = tk.Menu(self.master)  # create main menu bar
        self.master.configure(menu=self.__menubar)  # should be BEFORE iconbitmap, it's important
        # Add menubar to the main window BEFORE iconbitmap command. Otherwise it will shrink
        # in height by 20 pixels after each opening of the window.
        this_dir = os.path.dirname(os.path.realpath(__file__))  # directory of this file
        self.master.iconbitmap(os.path.join(this_dir, 'logo.ico'))  # set logo icon
        #
        self.__is_fullscreen = False  # enable / disable fullscreen mode
        self.__empty_menu = tk.Menu(self)  # empty menu to hide the real menubar in fullscreen mode
        self.__bugfix = False  # BUG! when change: fullscreen --> zoomed --> normal
        self.__previous_state = 0  # previous state of the event
        # List of shortcuts in the following format: [name, keycode, function]
        self.__shortcuts = [['Ctrl+O', 79, self.__open_image],   # 1 open image
                            ['Ctrl+W', 87, self.__close_image]]  # 2 close image
        # Bind events to the main window
        self.master.bind('<Motion>', self.__motion)  # track and handle mouse pointer position
        self.master.bind('<F11>', self.__fullscreen_toggle)  # toggle fullscreen mode
        self.master.bind('<Escape>', lambda e=None, s=False: self.__fullscreen_toggle(e, s))
        self.master.bind('<F5>', self.__default_geometry)  # reset default window geometry
        # Handle main window resizing in the idle mode, because consecutive keystrokes <F11> - <F5>
        # don't set default geometry from full screen if resizing is not postponed.
        self.master.bind('<Configure>', lambda event: self.master.after_idle(
            self.__resize_master, event))  # window is resized
        # Handle keystrokes in the idle mode, because program slows down on a weak computers,
        # when too many key stroke events in the same time.
        self.master.bind('<Key>', lambda event: self.master.after_idle(self.__keystroke, event))

    def __fullscreen_toggle(self, event=None, state=None):
        """ Enable/disable the fullscreen mode """
        if state is not None:
            self.__is_fullscreen = state
        else:
            self.__is_fullscreen = not self.__is_fullscreen  # toggling the boolean
        # Hide menubar in fullscreen mode or show it otherwise
        if self.__is_fullscreen:
            self.__menubar_hide()
        else:  # show menubar
            self.__menubar_show()
        self.master.wm_attributes('-fullscreen', self.__is_fullscreen)  # fullscreen mode on/off

    def __menubar_show(self):
        """ Show menu bar """
        self.master.configure(menu=self.__menubar)

    def __menubar_hide(self):
        """ Hide menu bar """
        self.master.configure(menu=self.__empty_menu)

    def __motion(self, event):
        """ Track mouse pointer and handle its position """
        if self.__is_fullscreen:
            y = self.master.winfo_pointery()
            if 0 <= y < 20:  # if close to the upper side of the main window
                self.__menubar_show()
            else:
                self.__menubar_hide()

    def __keystroke(self, event):
        """ Language independent handle events from the keyboard
            Link1: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/key-names.html
            Link2: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/event-handlers.html """
        #print(event.keycode, event.keysym, event.state)  # uncomment it for debug purposes
        if event.state - self.__previous_state == 4:  # check if <Control> key is pressed
            for shortcut in self.__shortcuts:
                if event.keycode == shortcut[1]:
                    shortcut[2]()
        else:  # remember previous state of the event
            self.__previous_state = event.state

    def __default_geometry(self, event=None):
        """ Reset default geomentry for the main GUI window """
        self.__fullscreen_toggle(state=False)  # exit from fullscreen
        self.master.wm_state(self.__config.default_state)  # exit from zoomed
        self.__config.set_win_geometry(self.__config.default_geometry)  # save default to config
        self.master.geometry(self.__config.default_geometry)  # set default geometry

    def __resize_master(self, event=None):
        """ Save main window size and position into config file.
            There is a bug when changing window from fullscreen to zoomed and then to normal mode.
            Main window somehow remembers zoomed mode as normal, so I have to explicitly set
            previous geometry from config INI file to the main window. """
        if self.master.wm_attributes('-fullscreen'):  # don't remember fullscreen
            self.__bugfix = True  # fixing bug
            return
        if self.master.state() == 'normal':
            if self.__bugfix is True:  # fixing bug for: fullscreen --> zoomed --> normal
                self.__bugfix = False
                # Explicitly set previous geometry to fix the bug
                self.master.geometry(self.__config.get_win_geometry())
                return
            self.__config.set_win_geometry(self.master.winfo_geometry())
        self.__config.set_win_state(self.master.wm_state())

    def __create_widgets(self):
        """ Widgets for GUI are created here """
        # Enable/disable these menu labels in the main window
        self.__label_recent = 'Open recent'
        self.__label_close = 'Close image'
        # Create menu for the image.
        self.__image_menu = tk.Menu(self.__menubar, tearoff=False, postcommand=self.__list_recent)
        self.__image_menu.add_command(label='Open image', command=self.__shortcuts[0][2],
                                      accelerator=self.__shortcuts[0][0])
        self.__recent_images = tk.Menu(self.__image_menu, tearoff=False)
        self.__image_menu.add_cascade(label=self.__label_recent, menu=self.__recent_images)
        self.__image_menu.add_command(label=self.__label_close, command=self.__shortcuts[1][2],
                                      accelerator=self.__shortcuts[1][0], state='disabled')
        self.__menubar.add_cascade(label='File', menu=self.__image_menu)
        self.__image_menu.add_separator()
        self.__image_menu.add_command(label='Exit', command=self.destroy, accelerator=u'Alt+F4')
        # Create menu for the view: fullscreen, default size, etc.
        self.__view_menu = tk.Menu(self.__menubar, tearoff=False)
        self.__view_menu.add_command(label='Fullscreen', command=self.__fullscreen_toggle,
                                     accelerator='F11')
        self.__view_menu.add_command(label='Default size', command=self.__default_geometry,
                                     accelerator='F5')
        self.__menubar.add_cascade(label='View', menu=self.__view_menu)
        # Create placeholder frame for the image
        self.master.rowconfigure(0, weight=1)  # make grid cell expandable
        self.master.columnconfigure(0, weight=1)
        self.__placeholder = ttk.Frame(self.master)
        self.__placeholder.grid(row=0, column=0, sticky='nswe')
        self.__placeholder.rowconfigure(0, weight=1)  # make grid cell expandable
        self.__placeholder.columnconfigure(0, weight=1)
        # If image wasn't closed previously, open this image once again
        path = self.__config.get_opened_path()
        if path:
            self.__set_image(path)  # open previous image

    def __list_recent(self):
        """ List of the recent images """
        self.__recent_images.delete(0, 'end')  # empty previous list
        l = self.__config.get_recent_list()  # get list of recently opened images
        for path in l:  # get list of recent image paths
            self.__recent_images.add_command(label=path, command=lambda x=path: self.__set_image(x))
        # Disable recent list menu if it is empty.
        if self.__recent_images.index('end') is None:
            self.__image_menu.entryconfigure(self.__label_recent, state='disabled')
        else:
            self.__image_menu.entryconfigure(self.__label_recent, state='normal')

    def __set_image(self, path):
        """ Close previous image and set a new one """
        self.__close_image()  # close previous image
        self.__imframe = ImageFrame(placeholder=self.__placeholder, path=path,
                                    roi_size=self.__config.get_roi_size())
        self.master.title(self.__default_title + ': {}'.format(path))  # change window title
        self.__config.set_recent_path(path)  # save image path into config
        # Enable 'Close image' submenu of the 'File' menu
        self.__image_menu.entryconfigure(self.__label_close, state='normal')

    @handle_exception(0)
    def __open_image(self):
        """ Open image in Image Viewer """
        path = askopenfilename(title='Select an image for the flight task',
                               initialdir=self.__config.get_recent_path())
        if path == '': return
        # Check if it is an image
        try:  # try to open and close image with PIL
            img = Image.open(path)
            img.close()
        except:
            messagebox.showinfo('Not an image',
                                'This is not an image: "{}"\nPlease, select an image.'.format(path))
            self.__open_image()  # try to open new image again
            return
        #
        self.__set_image(path)

    def __close_image(self):
        """ Close image """
        if self.__imframe:
            self.__imframe.destroy()
            self.__imframe = None
            self.master.title(self.__default_title)  # set default window title
            # Disable 'Close image' submenu of the 'File' menu
            self.__image_menu.entryconfigure(self.__label_close, state='disabled')

    def destroy(self):
        """ Destroy the main frame object and release all resources """
        if self.__imframe:  # image is not closed
            self.__config.set_opened_path(self.__imframe.path)  # remember opened image
        else:  # image is closed
            self.__config.set_opened_path()  # no path
        self.__close_image()
        self.__config.destroy()
        logging.info('Close GUI')
        self.quit()
