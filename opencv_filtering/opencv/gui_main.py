# -*- coding: utf-8 -*-
import os
import cv2
import tkinter as tk

from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk
from .gui_menu import Menu
from .logic_config import Config
from .logic_camera import Camera
from .logic_filters import Filters
from .gui_tooltip import ToolTip
from .logic_logger import logging


class MainGUI(ttk.Frame):
    """ Main GUI Window """
    def __init__(self, mainframe):
        """ Initialize the Frame """
        ttk.Frame.__init__(self, master=mainframe)
        # Create instances: config and filters
        self.master.title('OpenCV Filtering')  # set window title
        self.output_path = 'temp'  # store output path
        self.config = Config(path=self.output_path)  # open config file of the main window
        # Create OpenCV filters object
        self.filters = Filters(master=self.master, filter_num=self.config.get_current_filter())
        self.camera = Camera(current=self.config.get_current_camera())  # create web camera object
        #
        self.this_dir = os.path.dirname(os.path.realpath(__file__))  # directory of this file
        self._menu = None  # menu widget
        self.buttons = None  # buttons at the bottom of the GUI
        self.fullscreen = False  # enable/disable fullscreen mode
        self._bugfix = False  # BUG! when change: fullscreen --> zoomed --> normal
        self._filter = Image.ANTIALIAS  # could be: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
        self.previous_state = 0  # previous state of the event
        self.shortcuts = None  # define hot-keys
        self.ctrl_shortcuts = None
        self.current_frame = None  # current frame from the camera
        self.panel = None  # image panel
        #
        self.create_main_window()
        self.create_widgets()
        self.video_loop()  # constantly pool the video sensor for recent frame

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        if self.camera is not None:  # BUG! If plug out camera 'ok' is True after next 30 ms callback
            ok, frame = self.camera.read()  # read frame from the video stream
            if ok:  # frame captured without any errors
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # convert colors from BGR to RGB
                frame = self.filters.convert(frame)  # convert frame with the current OpenCV filter
                try:
                    self.current_frame = Image.fromarray(frame)  # convert image for PIL
                except (AttributeError, ValueError):
                    logging.warning(f'No frame for filter {self.filters.get_filter()}')
                image = self.resize_image(self.current_frame)  # resize image for the GUI window
                imgtk = ImageTk.PhotoImage(image=image)  # convert image for tkinter
                self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
                self.panel.config(image=imgtk)  # show the image
            else:  # destroy camera object
                self.camera.destroy()
                self.camera = None
                self.current_frame = None
                self.panel.imgtk = None  # clear image panel
                self.panel.config(image=None)
        else:  # try to create new camera object again, because camera.read() is True on the next callback
            self.camera = Camera(current=self.config.get_current_camera())  # create web camera object
            self.shortcuts['camera'][1] = self.camera  # replace shortcuts object for the menu
            self._menu = Menu(self.master, shortcuts=self.shortcuts)  # recreate menu bar
            self.master.configure(menu=self._menu.menubar)
        self.master.after(30, self.video_loop)  # call the same function after 30 milliseconds

    def create_main_window(self):
        """ Create main window GUI """
        logging.info('Open GUI')
        self.master.geometry(self.config.get_win_geometry())  # get window size/position from config
        self.master.wm_state(self.config.get_win_state())  # get window state
        # self.destroy function gets fired when the window is closed
        self.master.protocol('WM_DELETE_WINDOW', self.destroy)
        #
        if os.name == 'nt':  # Windows OS
            keycode = {
                's': [83],
                '→': [68, 39, 102, 34],  # keys: 'd', 'Right', scroll right, PageDown
                '←': [65, 37, 100, 33],  # keys: 'a', 'Left', scroll left, PageUp
            }
        else:  # Linux OS
            keycode = {
                's': [39],
                '→': [40, 114, 85],
                '←': [38, 113, 83],
            }
        # Dictionary of shortcuts in the following format:
        # name: [menu_string, function, hotkey, keycode_list]
        self.shortcuts = {
            'next': ['Next Filter', self.filters.next_filter, '→', keycode['→']],  # set next filter
            'last': ['Last Filter', self.filters.last_filter, '←', keycode['←']],  # set last filter
            'save': ['Take Snapshot', self.take_snapshot, 'Ctrl+S', keycode['s']],  # save snapshot
            'exit': ['Exit', self.destroy, 'Alt+F4'],  # close GUI
            'filters': ['Filters', self.filters],  # filters object
            'camera': ['Camera', self.camera],  # camera object
            'fullscreen': ['Fullscreen', self.toggle_fullscreen, 'F11'],  # full screen mode
            'default': ['Default Size', self.default_geometry, 'F5'],  # default GUI parameters
        }
        self.ctrl_shortcuts = [self.shortcuts['save']]  # shortcuts with <Ctrl> key pressed
        self.master.bind('<MouseWheel>', self.wheel)  # mouse wheel for Windows and MacOS, but not Linux
        self.master.bind('<Button-5>',   self.wheel)  # mouse wheel for Linux, scroll down
        self.master.bind('<Button-4>',   self.wheel)  # mouse wheel for Linux, scroll up
        self.master.bind('<Motion>', lambda event: self.motion())  # track and handle mouse pointer position
        self.master.bind('<F11>', lambda event: self.toggle_fullscreen())  # toggle fullscreen mode
        self.master.bind('<Escape>', lambda event, s=False: self.toggle_fullscreen(s))
        self.master.bind('<F5>', lambda event: self.default_geometry())  # reset default window geometry
        # Handle window resizing in the idle mode, because consecutive keystrokes <F11> - <F5>
        # don't set default geometry from full screen if resizing is not postponed.
        self.master.bind('<Configure>', lambda event: self.master.after_idle(self.resize_window))
        # Handle keystrokes in the idle mode, because program slows down on a weak computers,
        # when too many key stroke events in the same time.
        self.master.bind('<Key>', lambda event: self.master.after_idle(self.keystroke, event))

    def take_snapshot(self):
        """ Take snapshot and save it to the file """
        uid = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')  # unique ID from the current timestamp
        filename = f'{uid}.png'  # construct filename from UID
        filepath = os.path.join(self.output_path, filename)  # construct output path
        self.current_frame.save(filepath)  # save image frame as PNG file
        logging.info(f'Snapshot saved to {filepath}')
        return filepath

    def wheel(self, event):
        """ Mouse wheel event """
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            self.filters.next_filter()
        if event.num == 4 or event.delta == 120:  # scroll up
            self.filters.last_filter()

    def toggle_fullscreen(self, state=None):
        """ Enable/disable the full screen mode """
        # Toggle the boolean self.fullscreen
        if state is not None:
            self.fullscreen = state
        else:
            self.fullscreen = not self.fullscreen
        # Hide menubar in fullscreen mode or show it otherwise
        if self.fullscreen:
            self.hide_menu()
            self.buttons.grid_forget()
        else:
            self.show_menu()
            self.buttons.grid(row=1, column=0)
        self.master.wm_attributes('-fullscreen', self.fullscreen)  # fullscreen mode on/off

    def show_menu(self):
        """ Show menu bar """
        self.master.configure(menu=self._menu.menubar)

    def hide_menu(self):
        """ Hide menu bar """
        self.master.configure(menu=self._menu.empty_menu)

    def motion(self):
        """ Track mouse pointer and handle its position """
        if self.fullscreen:
            y = self.master.winfo_pointery()
            # Show menu if close to the upper side of the main window or hide it otherwise
            self.show_menu() if (0 <= y < 20) else self.hide_menu()
            # Show buttons if close to the lower side of the main windows or hide them otherwise
            if self.master.winfo_height()-30 <= y:
                self.buttons.grid(row=1, column=0)
            else:
                self.buttons.grid_forget()

    def default_geometry(self):
        """ Reset default geometry for the main GUI window """
        self.toggle_fullscreen(state=False)  # exit from fullscreen
        self.master.wm_state(self.config.default_state)  # exit from zoomed
        self.master.geometry(self.config.default_geometry)  # set default geometry
        self.config.set_win_geometry(self.config.default_geometry)  # save default to config
        self.camera.set_resolution(0)  # set default resolution

    def resize_window(self):
        """ Save main window size and position into config file.
            BUG! There is a BUG when changing window from fullscreen to zoomed and then to normal mode.
            Main window somehow remembers zoomed mode as normal, so I have to explicitly set
            previous geometry from config INI file to the main window. """
        if self.master.wm_attributes('-fullscreen'):  # don't remember fullscreen geometry
            self._bugfix = True  # fixing bug
            return
        if self.master.state() == 'normal':
            if self._bugfix is True:  # fixing bug for: fullscreen --> zoomed --> normal
                self._bugfix = False
                # Explicitly set previous geometry to fix the bug
                self.master.geometry(self.config.get_win_geometry())
                return
            self.config.set_win_geometry(self.master.winfo_geometry())
        self.config.set_win_state(self.master.wm_state())

    def keystroke(self, event):
        """ Language independent handle events from the keyboard """
        # print(event.keycode, event.keysym, event.state)  # uncomment it for debug purposes
        if event.state - self.previous_state == 4:  # check if <Ctrl> key is pressed
            for s in self.ctrl_shortcuts:  # for all <Ctrl> shortcuts
                if event.keycode in s[3]:  # if <Ctrl> key is pressed
                    s[1]()  # execute a function
        else:  # <Ctrl> key is not pressed
            self.previous_state = event.state  # remember previous state of the event
            if event.keycode in self.shortcuts['next'][3]:  # keycode is pressed
                self.shortcuts['next'][1]()  # next filter
            elif event.keycode in self.shortcuts['last'][3]:  # keycode is pressed
                self.shortcuts['last'][1]()  # last filter

    def create_widgets(self):
        """ Widgets for GUI are created here """
        self._menu = Menu(self.master, shortcuts=self.shortcuts)
        self.master.configure(menu=self._menu.menubar)
        if os.name == 'nt':  # Windows OS
            self.master.iconbitmap(os.path.join(self.this_dir, 'logo.ico'))  # set logo icon
        else:  # Linux OS
            # ICO format does not work for Linux. Use GIF or black and white XBM format instead
            img = tk.PhotoImage(file=os.path.join(self.this_dir, 'logo.gif'))
            # noinspection PyProtectedMember
            self.master.tk.call('wm', 'iconphoto', self.master._w, img)  # set logo icon
        # Create ttk.Frame container in GUI and make it expandable
        container = ttk.Frame(self.master)
        container.pack(fill=tk.BOTH, expand=1)
        # Configure the rows and columns to have a non-zero weight so that they will take up the extra space
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        self.panel = ttk.Label(container, text='Web camera image', anchor='center')  # initialize image panel
        self.panel.grid(row=0, column=0, sticky='nswe')  # make ttk.Label expandable
        self.buttons = ttk.Label(container)  # initialize buttons panel
        self.buttons.grid(row=1, column=0)
        self.add_button(master=self.buttons, name='icon_arrow_left.png', text=self.shortcuts['last'][0],
                        command=self.shortcuts['last'][1])
        self.add_button(master=self.buttons, name='icon_save_image.png', text=self.shortcuts['save'][0],
                        command=self.shortcuts['save'][1])
        self.add_button(master=self.buttons, name='icon_arrow_right.png', text=self.shortcuts['next'][0],
                        command=self.shortcuts['next'][1])

    def add_button(self, master, name, text, command):
        """ Add button to the GUI """
        path = os.path.join(self.this_dir, name)
        image = Image.open(path)
        image = image.resize((20, 20))
        image = ImageTk.PhotoImage(image)
        button = ttk.Button(master, text=text, image=image, command=command)
        button.pack(side=tk.LEFT)
        button.save = image  # anchor image so it does not be deleted by the garbage-collector
        ToolTip(button, msg=text)  # set tooltip to the button

    def resize_image(self, image):
        """ Resize image proportionally """
        w1, h1 = image.size
        w1, h1 = float(w1), float(h1)
        w2, h2 = float(self.panel.winfo_width()), float(self.panel.winfo_height())
        aspect_ratio1 = w1 / h1
        aspect_ratio2 = w2 / h2
        if aspect_ratio1 == aspect_ratio2:
            return image.resize((int(w2), int(h2)), self._filter)
        elif aspect_ratio1 > aspect_ratio2:
            return image.resize((int(w2), max(1, int(w2 / aspect_ratio1))), self._filter)
        else:  # aspect_ratio1 < aspect_ratio2
            return image.resize((max(1, int(h2 * aspect_ratio1)), int(h2)), self._filter)

    def destroy(self):
        """ Destroy the main frame object and release all resources """
        self.config.set_current_filter(self.filters.current_filter)  # save current filter
        if self.camera is not None:
            self.config.set_current_camera(self.camera.current_camera)  # save current web camera
            self.camera.destroy()
        self.config.destroy()
        logging.info('Close GUI')
        self.quit()
