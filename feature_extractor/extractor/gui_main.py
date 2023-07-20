import os
import cv2
import tkinter as tk

from PIL import Image
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from .gui_menu import Menu
from .gui_display import Display
from .logic_config import Config
from .logic_extractor import FeatureExtractor
from .logic_logger import logging, handle_exception


class MainGUI:
    """ Main GUI Window """
    def __init__(self):
        """ Initialize the Frame """
        logging.info('Open GUI')
        self.gui = tk.Tk()  # initialize root window
        self.__create_instances()
        self.__create_main_window()
        self.__create_widgets()

    def __create_instances(self):
        """ Instances for GUI are created here """
        self._config = Config()  # open config file of the main window
        subclasses = FeatureExtractor.__subclasses__()  # get list of all subclasses of the abstract class
        self._extractor = subclasses[0](self._config.get_recent_image())  # feature extractors

    def __create_main_window(self):
        """ Create main window GUI"""
        self.__default_title = 'Feature extractor: '
        self.gui.title(self.__default_title)  # set window title
        # Get window size/position from config INI file: 'Width × Height ± X ± Y'
        self.gui.geometry(self._config.get_win_geometry())
        self.gui.wm_state(self._config.get_win_state())  # get window state
        # Trigger self.destructor function when the root window is closed
        self.gui.protocol('WM_DELETE_WINDOW', self.destroy)
        #
        self.__fullscreen = False  # enable / disable fullscreen mode
        self.__bugfix = False  # BUG! when change: fullscreen --> zoomed --> normal
        self.__previous_state = 0  # previous state of the event
        # List of shortcuts in the following format: [name, keycode, function]
        self.keycode = {}  # init key codes
        if os.name == 'nt':  # Windows OS
            self.keycode = {
                'o': 79,
            }
        else:  # Linux OS
            self.keycode = {
                'o': 32,
            }
        self._shortcuts = [
            ['Ctrl+O', self.keycode['o'], self.__open_image],  # open image
        ]
        # Bind events to the main window
        self.gui.bind('<Motion>', lambda event: self.__motion())  # track and handle mouse pointer position
        self.gui.bind('<F11>', lambda event: self._toggle_fullscreen())  # toggle fullscreen mode
        self.gui.bind('<Escape>', lambda event, s=False: self._toggle_fullscreen(s))
        self.gui.bind('<F5>', lambda event: self._default_geometry())  # reset default window geometry
        # Handle main window resizing in the idle mode, because consecutive keystrokes <F11> - <F5>
        # don't set default geometry from fullscreen if resizing is not postponed.
        self.gui.bind('<Configure>', lambda event: self.gui.after_idle(self.__resize_master))
        # Handle keystrokes in the idle mode, because program slows down on a weak computers,
        # when too many keystroke events in the same time.
        self.gui.bind('<Key>', lambda event: self.gui.after_idle(self.__keystroke, event))

    def _toggle_fullscreen(self, state=None):
        """ Enable/disable the fullscreen mode """
        if state is not None:
            self.__fullscreen = state  # set state to fullscreen
        else:
            self.__fullscreen = not self.__fullscreen  # toggling the boolean
        # Hide menubar in fullscreen mode or show it otherwise
        if self.__fullscreen:
            self.__menubar_hide()
        else:  # show menubar
            self.__menubar_show()
        self.gui.wm_attributes('-fullscreen', self.__fullscreen)  # fullscreen mode on/off

    def __menubar_show(self):
        """ Show menu bar """
        self.gui.configure(menu=self.__menu.menubar)

    def __menubar_hide(self):
        """ Hide menu bar """
        self.gui.configure(menu=self.__menu.empty_menu)

    def __motion(self):
        """ Track mouse pointer and handle its position """
        if self.__fullscreen:
            y = self.gui.winfo_pointery()
            if 0 <= y < 20:  # if close to the upper side of the main window
                self.__menubar_show()
            else:
                self.__menubar_hide()

    def __keystroke(self, event):
        """ Language independent handle events from the keyboard """
        # print(event.keycode, event.keysym, event.state)  # uncomment it for debug purposes
        if event.state - self.__previous_state == 4:  # check if <Control> key is pressed
            for shortcut in self._shortcuts:
                if event.keycode == shortcut[1]:
                    shortcut[2]()
        else:  # remember previous state of the event
            self.__previous_state = event.state

    def _default_geometry(self):
        """ Reset default geometry for the main GUI window """
        self._toggle_fullscreen(state=False)  # exit from fullscreen
        self.gui.wm_state(self._config.default_state)  # exit from zoomed
        self._config.set_win_geometry(self._config.default_geometry)  # save default to config
        self.gui.geometry(self._config.default_geometry)  # set default geometry

    def __resize_master(self):
        """ Save main window size and position into config file.
            BUG! There is a BUG when changing window from fullscreen to zoomed and then to normal mode.
            Main window somehow remembers zoomed mode as normal, so I have to explicitly set
            previous geometry from config INI file to the main window. """
        if self.gui.wm_attributes('-fullscreen'):  # don't remember fullscreen geometry
            self.__bugfix = True  # fixing bug
            return
        if self.gui.state() == 'normal':
            if self.__bugfix is True:  # fixing bug for: fullscreen --> zoomed --> normal
                self.__bugfix = False
                # Explicitly set previous geometry to fix the bug
                self.gui.geometry(self._config.get_win_geometry())
                return
            self._config.set_win_geometry(self.gui.winfo_geometry())
        self._config.set_win_state(self.gui.wm_state())

    def __create_widgets(self):
        """ Widgets for GUI are created here """
        # Create menu widget
        self.__menu = Menu(self)
        self.gui.configure(menu=self.__menu.menubar)  # menu should be BEFORE iconbitmap, it's a bug
        # BUG! Add menu bar to the main window BEFORE iconbitmap command. Otherwise, it will
        # shrink in height by 20 pixels after each open-close of the main window.
        this_dir = os.path.dirname(os.path.realpath(__file__))  # directory of this file
        if os.name == 'nt':  # Windows OS
            self.gui.iconbitmap(os.path.join(this_dir, 'logo.ico'))  # set logo icon
        else:  # Linux OS
            # ICO format does not work for Linux. Use GIF or black and white XBM format instead.
            img = tk.PhotoImage(file=os.path.join(this_dir, 'logo.gif'))
            self.gui.tk.call('wm', 'iconphoto', self.gui._w, img)  # set logo icon
        # Create GUI display
        self.__display = Display(self)

    def _set_image(self, path):
        """ Close previous image and set a new one """
        self._config.set_recent_image(path)  # save image path into config
        self._extractor.set_image(cv2.imread(path))  # update image to track

    @handle_exception(0)
    def __open_image(self):
        """ Open image in the GUI """
        path = askopenfilename(title='Select an image', initialdir=self._config.get_recent_dir())
        if path == '':
            return
        if not self.is_image(path):  # check if it is an image
            messagebox.showinfo('Not an image', f'This is not an image: "{path}"\nPlease, select an image.')
            self.__open_image()  # try to open new image again
            return
        self._set_image(path)

    @staticmethod
    def is_image(path):
        """ Check if it is an image. Static method """
        try:  # try to open and close image with PIL
            img = Image.open(path)
            img.close()
        except FileNotFoundError or OSError:
            return False  # not an image
        return True  # image

    def destroy(self):
        """ Destroy the main frame object and release all resources """
        logging.info('Close GUI')
        self._config.destroy()
        self.__display.destroy()
        self.gui.quit()
