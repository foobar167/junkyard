# -*- coding: utf-8 -*-
import os
import warnings

from PIL import Image
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from .gui_menu import Menu
from .gui_polygons import Polygons
from .logic_config import Config
from .logic_logger import logging, handle_exception

class MainGUI(ttk.Frame):
    """ Main GUI Window """
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
        self.__is_fullscreen = False  # enable / disable fullscreen mode
        self.__bugfix = False  # BUG! when change: fullscreen --> zoomed --> normal
        self.__previous_state = 0  # previous state of the event
        # List of shortcuts in the following format: [name, keycode, function]
        self.__shortcuts = [['Ctrl+O', 79, self.__open_image],   # 1 open image
                            ['Ctrl+W', 87, self.__close_image],  # 2 close image
                            ['Ctrl+R', 82, self.__roll]]         # 3 rolling window
        # Bind events to the main window
        self.master.bind('<Motion>', lambda event: self.__motion())  # track and handle mouse pointer position
        self.master.bind('<F11>', lambda event: self.__fullscreen_toggle())  # toggle fullscreen mode
        self.master.bind('<Escape>', lambda event, s=False: self.__fullscreen_toggle(s))
        self.master.bind('<F5>', lambda event: self.__default_geometry())  # reset default window geometry
        # Handle main window resizing in the idle mode, because consecutive keystrokes <F11> - <F5>
        # don't set default geometry from full screen if resizing is not postponed.
        self.master.bind('<Configure>', lambda event: self.master.after_idle(self.__resize_master))
        # Handle keystrokes in the idle mode, because program slows down on a weak computers,
        # when too many key stroke events in the same time.
        self.master.bind('<Key>', lambda event: self.master.after_idle(self.__keystroke, event))

    def __fullscreen_toggle(self, state=None):
        """ Enable/disable the full screen mode """
        if state is not None:
            self.__is_fullscreen = state  # set state to fullscreen
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
        self.master.configure(menu=self.__menu.menubar)

    def __menubar_hide(self):
        """ Hide menu bar """
        self.master.configure(menu=self.__menu.empty_menu)

    def __motion(self):
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

    def __default_geometry(self):
        """ Reset default geomentry for the main GUI window """
        self.__fullscreen_toggle(state=False)  # exit from fullscreen
        self.master.wm_state(self.__config.default_state)  # exit from zoomed
        self.__config.set_win_geometry(self.__config.default_geometry)  # save default to config
        self.master.geometry(self.__config.default_geometry)  # set default geometry

    def __resize_master(self):
        """ Save main window size and position into config file.
            BUG! There is a BUG when changing window from fullscreen to zoomed and then to normal mode.
            Main window somehow remembers zoomed mode as normal, so I have to explicitly set
            previous geometry from config INI file to the main window. """
        if self.master.wm_attributes('-fullscreen'):  # don't remember fullscreen geometry
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
        # Create menu widget
        self.functions = {  # dictionary of functions for menu widget
            "destroy": self.destroy,
            "fullscreen_toggle": self.__fullscreen_toggle,
            "default_geometry": self.__default_geometry,
            "set_image": self.__set_image,
            "check_polygons": self.__check_polygons}
        self.__menu = Menu(self.master, self.__config, self.__shortcuts, self.functions)
        self.master.configure(menu=self.__menu.menubar)  # menu should be BEFORE iconbitmap, it's a bug
        # BUG! Add menu bar to the main window BEFORE iconbitmap command. Otherwise it will
        # shrink in height by 20 pixels after each open-close of the main window.
        this_dir = os.path.dirname(os.path.realpath(__file__))  # directory of this file
        self.master.iconbitmap(os.path.join(this_dir, 'logo.ico'))  # set logo icon
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

    def __set_image(self, path):
        """ Close previous image and set a new one """
        self.__close_image()  # close previous image
        self.__imframe = Polygons(placeholder=self.__placeholder, path=path)  # create image frame
        self.__imframe.grid()  # show it
        self.master.title(self.__default_title + ': {}'.format(path))  # change window title
        self.__config.set_recent_path(path)  # save image path into config
        # Enable 'Close image' submenu of the 'File' menu
        self.__menu.set_file(state='normal')

    @handle_exception(0)
    def __open_image(self):
        """ Open image in Image Viewer """
        path = askopenfilename(title='Select an image for the flight task',
                               initialdir=self.__config.get_recent_path())
        if path == '': return
        # Check if it is an image
        # noinspection PyBroadException
        try:  # try to open and close image with PIL
            with warnings.catch_warnings():  # suppress DecompressionBombWarning for the big image
                warnings.simplefilter(u'ignore')
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
            self.__menu.set_file(state='disabled')

    def __check_polygons(self):
        """ Check if there are polygons on the image """
        if self.__imframe and len(self.__imframe.poly_dict):  # if there are polygons
            return True
        return False  # if there are no polygons

    def __roll(self):
        """ Apply rolling window to polygons on the image """
        if self.__check_polygons():  # there are polygons
            for polygon in self.__imframe.poly_dict.values():  # for all values of the dictionary
                print(polygon)
            print('\n')

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
