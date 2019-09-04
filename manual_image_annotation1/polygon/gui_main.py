# -*- coding: utf-8 -*-
import os
import tkinter as tk

from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from .gui_menu import Menu
from .gui_polygons import Polygons
from .logic_config import Config
from .logic_logger import logging, handle_exception
from .logic_tools import get_images, save_polygons, open_polygons

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
        """ Create main window GUI """
        self.__default_title = 'Manual image annotation with polygons'
        self.master.title(self.__default_title)
        self.master.geometry(self.__config.get_win_geometry())  # get window size/position from config
        self.master.wm_state(self.__config.get_win_state())  # get window state
        # self.destructor gets fired when the window is destroyed
        self.master.protocol('WM_DELETE_WINDOW', self.destroy)
        #
        self.__fullscreen = False  # enable / disable fullscreen mode
        self.__bugfix = False  # BUG! when change: fullscreen --> zoomed --> normal
        self.__previous_state = 0  # previous state of the event
        # List of shortcuts in the following format: [name, keycode, function]
        self.keycode = {}  # init key codes
        if os.name == 'nt':  # Windows OS
            self.keycode = {
                'o': 79,
                'w': 87,
                'r': 82,
                'q': 81,
                'h': 72,
                's': 83,
                'a': 65,
            }
        else:  # Linux OS
            self.keycode = {
                'o': 32,
                'w': 25,
                'r': 27,
                'q': 24,
                'h': 43,
                's': 39,
                'a': 38,
            }
        self.__shortcuts = [['Ctrl+O', self.keycode['o'], self.__open_image],   # 0 open image
                            ['Ctrl+W', self.keycode['w'], self.__close_image],  # 1 close image
                            ['Ctrl+R', self.keycode['r'], self.__roll],         # 2 rolling window
                            ['Ctrl+Q', self.keycode['q'], self.__toggle_poly],  # 3 toggle between roi/hole drawing
                            ['Ctrl+H', self.keycode['h'], self.__open_poly],    # 4 open polygons for the image
                            ['Ctrl+S', self.keycode['s'], self.__save_poly],    # 5 save polygons of the image
                            ['Ctrl+A', self.keycode['a'], self.__show_rect]]    # 6 show rolling window rectangle
        # Bind events to the main window
        self.master.bind('<Motion>', lambda event: self.__motion())  # track and handle mouse pointer position
        self.master.bind('<F11>', lambda event: self.__toggle_fullscreen())  # toggle fullscreen mode
        self.master.bind('<Escape>', lambda event, s=False: self.__toggle_fullscreen(s))
        self.master.bind('<F5>', lambda event: self.__default_geometry())  # reset default window geometry
        # Handle main window resizing in the idle mode, because consecutive keystrokes <F11> - <F5>
        # don't set default geometry from full screen if resizing is not postponed.
        self.master.bind('<Configure>', lambda event: self.master.after_idle(self.__resize_master))
        # Handle keystrokes in the idle mode, because program slows down on a weak computers,
        # when too many key stroke events in the same time.
        self.master.bind('<Key>', lambda event: self.master.after_idle(self.__keystroke, event))

    def __toggle_fullscreen(self, state=None):
        """ Enable/disable the full screen mode """
        if state is not None:
            self.__fullscreen = state  # set state to fullscreen
        else:
            self.__fullscreen = not self.__fullscreen  # toggling the boolean
        # Hide menubar in fullscreen mode or show it otherwise
        if self.__fullscreen:
            self.__menubar_hide()
        else:  # show menubar
            self.__menubar_show()
        self.master.wm_attributes('-fullscreen', self.__fullscreen)  # fullscreen mode on/off

    def __menubar_show(self):
        """ Show menu bar """
        self.master.configure(menu=self.__menu.menubar)

    def __menubar_hide(self):
        """ Hide menu bar """
        self.master.configure(menu=self.__menu.empty_menu)

    def __motion(self):
        """ Track mouse pointer and handle its position """
        if self.__fullscreen:
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
        self.__toggle_fullscreen(state=False)  # exit from fullscreen
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
            "toggle_fullscreen": self.__toggle_fullscreen,
            "default_geometry": self.__default_geometry,
            "set_image": self.__set_image,
            "check_roi": self.__check_roi}
        self.__menu = Menu(self.master, self.__config, self.__shortcuts, self.functions)
        self.master.configure(menu=self.__menu.menubar)  # menu should be BEFORE iconbitmap, it's a bug
        # BUG! Add menu bar to the main window BEFORE iconbitmap command. Otherwise it will
        # shrink in height by 20 pixels after each open-close of the main window.
        this_dir = os.path.dirname(os.path.realpath(__file__))  # directory of this file
        if os.name == 'nt':  # Windows OS
            self.master.iconbitmap(os.path.join(this_dir, 'logo.ico'))  # set logo icon
        else:  # Linux OS
            # ICO format does not work for Linux. Use GIF or black and white XBM format instead.
            img = tk.PhotoImage(file=os.path.join(this_dir, 'logo.gif'))
            self.master.tk.call('wm', 'iconphoto', self.master._w, img)  # set logo icon
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
        self.__imframe = Polygons(placeholder=self.__placeholder, path=path,
                                  roll_size=self.__config.get_roll_size())  # create image frame
        self.__imframe.grid()  # show it
        self.master.title(self.__default_title + ': {}'.format(path))  # change window title
        self.__config.set_recent_path(path)  # save image path into config
        # Enable some menus
        self.__menu.set_state(state='normal', roi=self.__imframe.roi, rect=self.__imframe.rect)

    @handle_exception(0)
    def __open_image(self):
        """ Open image in the GUI """
        path = askopenfilename(title='Select an image',
                               initialdir=self.__config.get_recent_path())
        if path == '': return
        # Check if it is an image
        if not Polygons.check_image(path):
            messagebox.showinfo('Not an image',
                                'This is not an image: "{}"\nPlease, select an image.'.format(path))
            self.__open_image()  # try to open new image again
            return
        #
        self.__set_image(path)

    def __close_image(self):
        """ Close image """
        if self.__imframe:
            if len(self.__imframe.roi_dict) + len(self.__imframe.hole_dict):
                self.__save_poly()  # if there are polygons, save them
            self.__imframe.destroy()
            self.__imframe = None
            self.master.title(self.__default_title)  # set default window title
            self.__menu.set_state(state='disabled')  # disable some menus

    def __check_roi(self):
        """ Check if there are ROI on the image """
        if self.__imframe and len(self.__imframe.roi_dict):  # there are ROI on the image
            return True
        return False  # if there are no polygons

    def __roll(self):
        """ Apply rolling window to ROI polygons on the image """
        if self.__check_roi():  # there are ROI
            get_images(self.__imframe, self.__config)  # get and save all images

    def __toggle_poly(self):
        """ Toggle between ROI and hole polygons drawing """
        if self.__imframe:
            self.__imframe.roi = not self.__imframe.roi  # toggle ROI or hole polygons drawing
            self.__menu.set_tools_toggle(self.__imframe.roi)  # change menu label

    def __open_poly(self):
        """ Open polygons ROI and holes for the current image from file """
        if self.__imframe:
            path = askopenfilename(title='Open polygons for the current image',
                                   initialdir=self.__config.config_dir)
            if path == '': return
            # noinspection PyBroadException
            try:  # check if it is a right file with polygons
                open_polygons(self.__imframe, path)
                self.__imframe.roi = True  # reset ROI drawing
                self.__menu.set_tools_toggle(self.__imframe.roi)  # change menu label
            except:
                messagebox.showinfo('Wrong file',
                                    'Wrong polygons for image: "{}"\n'.format(self.__imframe.path) +
                                    'Please, select polygons for the current image.')
                self.__open_poly()  # try to open polygons again
                return

    def __save_poly(self):
        """ Save polygons ROI and holes of the current image into file """
        if self.__imframe:
            save_polygons(self.__imframe, self.__config)

    def __show_rect(self):
        """ Show / hide rolling window rectangle """
        if self.__imframe:
            self.__imframe.rect = not self.__imframe.rect  # show / hide rolling window rectangle
            self.__menu.show_rect(self.__imframe.rect)  # change menu label

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
