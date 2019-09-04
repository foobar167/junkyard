# -*- coding: utf-8 -*-
# Take snapshot using web camera, OpenCV and Tkinter.
import os
import cv2
import datetime
import tkinter as tk

from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk
from .logic_logger import logging


class MainGUI(ttk.Frame):
    """ Main GUI Window """
    def __init__(self, mainframe):
        """ Initialize the Frame """
        logging.info('Open GUI')
        ttk.Frame.__init__(self, master=mainframe)
        #
        # 0 is default web camera, cv2.CAP_DSHOW is a flag DirectShow (via videoInput)
        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # capture video frames
        self.output_path = 'temp'  # store output path
        self.current_image = None  # current image from the camera
        self.panel = None  # image panel
        #
        self.create_main_window()
        self.create_widgets()
        self.video_loop()  # constantly pool the video sensor for recent frame

    def create_main_window(self):
        """ Create main window GUI """
        self.master.title('OpenCV Filtering')  # set window title
        # self.destroy function gets fired when the window is closed
        self.master.protocol('WM_DELETE_WINDOW', self.destroy)

    def create_widgets(self):
        """ Widgets for GUI are created here """
        self.panel = ttk.Label(self.master)  # initialize image panel
        self.panel.pack()
        # Buttons panel
        buttons = ttk.Label(self.master)
        buttons.pack()
        # Next filter button
        ttk.Button(buttons, text='Next filter').pack(side=tk.LEFT)
        # Button for snapshots
        ttk.Button(buttons, text='Take snapshot', command=self.take_snapshot).pack(side=tk.LEFT)
        # Last filter button
        ttk.Button(buttons, text='Last filter').pack(side=tk.LEFT)

    def take_snapshot(self):
        """ Take snapshot and save it to the file """
        uid = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')  # unique ID from the current timestamp
        filename = '{}.jpg'.format(uid)  # construct filename
        path = os.path.join(self.output_path, filename)  # construct output path
        self.current_image.save(path)  # save image as jpeg file
        this_dir = os.path.dirname(os.path.realpath(__file__))  # directory of this file
        path = os.path.join(this_dir, path)
        logging.info('Snapshot saved to {}'.format(path))

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

    def destroy(self):
        """ Destroy the main frame object and release all resources """
        logging.info('Close GUI')
        self.camera.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application
        self.quit()
