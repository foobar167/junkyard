# -*- coding: utf-8 -*-
# Take snapshot using web camera, OpenCV and Tkinter.
import os
import cv2
import datetime
import tkinter as tk

from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk
from .gui_menu import Menu
from .gui_tooltip import ToolTip
from .logic_logger import logging


class MainGUI(ttk.Frame):
    """ Main GUI Window """
    def __init__(self, mainframe):
        """ Initialize the Frame """
        if self.count_cameras() == 0:  # check for the web camera
            logging.info('No web camera on the computer')
            messagebox.showinfo('No web camera', 'There are no web cameras on your computer.\nExit from the GUI.')
            return
        logging.info('Open GUI')
        ttk.Frame.__init__(self, master=mainframe)
        # 0 is default web camera, cv2.CAP_DSHOW is a flag DirectShow (via videoInput)
        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # capture video frames
        self.this_dir = os.path.dirname(os.path.realpath(__file__))  # directory of this file
        self._menu = None  # menu widget
        self.previous_state = 0  # previous state of the event
        self.shortcuts = None  # define hotkeys
        self.output_path = 'temp'  # store output path
        self.current_image = None  # current image from the camera
        self.panel = None  # image panel
        #
        self.create_main_window()
        self.create_widgets()
        self.video_loop()  # constantly pool the video sensor for recent frame

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.camera.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # convert colors from BGR to RGB
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image
        self.master.after(30, self.video_loop)  # call the same function after 30 milliseconds

    @staticmethod
    def count_cameras():
        """ Get the number of cameras available """
        max_tested = 100  # maximum web cameras to test
        for i in range(max_tested):
            camera = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if camera.isOpened():
                camera.release()
                continue
            return i

    def create_main_window(self):
        """ Create main window GUI """
        self.master.title('OpenCV Filtering')  # set window title
        self.master.resizable(False, False)  # Tkinter window is not resizable
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
        # List of shortcuts in the following format: [name, function, hotkey, keycode, ctrl]
        self.shortcuts = [
            ['Take snapshot', self.take_snapshot, 'Ctrl+S', keycode['s'], True],   # 0 - take snapshot
            ['Next Filter',   self.next_filter,   '→',      keycode['→'], False],  # 1 - set next filter
            ['Last Filter',   self.last_filter,   '←',      keycode['←'], False],  # 2 - set last filter
            ['Exit',          self.destroy,       'Alt+F4', None,         False],  # 3 - close GUI
        ]
        self.master.bind('<MouseWheel>', self.wheel)  # mouse wheel for Windows and MacOS, but not Linux
        self.master.bind('<Button-5>',   self.wheel)  # mouse wheel for Linux, scroll down
        self.master.bind('<Button-4>',   self.wheel)  # mouse wheel for Linux, scroll up
        # Handle keystrokes in the idle mode, because program slows down on a weak computers,
        # when too many key stroke events in the same time.
        self.master.bind('<Key>', lambda event: self.master.after_idle(self.keystroke, event))

    def wheel(self, event):
        """ Mouse wheel event """
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            self.next_filter()
        if event.num == 4 or event.delta == 120:  # scroll up
            self.last_filter()

    def keystroke(self, event):
        """ Language independent handle events from the keyboard """
        # print(event.keycode, event.keysym, event.state)  # uncomment it for debug purposes
        if event.state - self.previous_state == 4:  # check if <Control> key is pressed
            for shortcut in self.shortcuts:  # for all shortcuts
                if shortcut[4] and event.keycode in shortcut[3]:  # if ctrl is True and key is pressed
                    shortcut[1]()  # execute a function
        else:  # <Control> key is not pressed
            self.previous_state = event.state  # remember previous state of the event
            if event.keycode in self.shortcuts[1][3]:
                self.shortcuts[1][1]()  # next filter
            elif event.keycode in self.shortcuts[2][3]:
                self.shortcuts[2][1]()  # last filter

    def create_widgets(self):
        """ Widgets for GUI are created here """
        self._menu = Menu(self.master, self.shortcuts)
        self.master.configure(menu=self._menu.menubar)
        if os.name == 'nt':  # Windows OS
            self.master.iconbitmap(os.path.join(self.this_dir, 'logo.ico'))  # set logo icon
        else:  # Linux OS
            # ICO format does not work for Linux. Use GIF or black and white XBM format instead
            img = tk.PhotoImage(file=os.path.join(self.this_dir, 'logo.gif'))
            # noinspection PyProtectedMember
            self.master.tk.call('wm', 'iconphoto', self.master._w, img)  # set logo icon
        self.panel = ttk.Label(self.master)  # initialize image panel
        self.panel.pack()
        buttons = ttk.Label(self.master)  # initialize buttons panel
        buttons.pack()
        self.add_button(master=buttons, name='icon_arrow__left.png', text=self.shortcuts[2][0], command=self.shortcuts[2][1])
        self.add_button(master=buttons, name='icon_save__image.png', text=self.shortcuts[0][0], command=self.shortcuts[0][1])
        self.add_button(master=buttons, name='icon_arrow_right.png', text=self.shortcuts[1][0], command=self.shortcuts[1][1])

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

    def next_filter(self):
        """ Set next OpenCV filter to the video loop """
        logging.info('Set next filter')

    def last_filter(self):
        """ Set last OpenCV filter to the video loop """
        logging.info('Set last filter')

    def take_snapshot(self):
        """ Take snapshot and save it to the file """
        uid = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')  # unique ID from the current timestamp
        filename = '{}.png'.format(uid)  # construct filename from UID
        path = os.path.join(self.output_path, filename)  # construct output path
        self.current_image.save(path)  # save image as jpeg file
        logging.info('Snapshot saved to {}'.format(path))

    def destroy(self):
        """ Destroy the main frame object and release all resources """
        logging.info('Close GUI')
        self.camera.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application
        self.quit()
