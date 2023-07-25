import os
import cv2
import tkinter as tk

from datetime import datetime
from PIL import Image, ImageTk
from .logic_logger import logging


class Display:
    """ Display canvas with image and button """
    def __init__(self, main_window):
        """ Set web camera, searchable image, snapshot button, etc. to display on GUI """
        self.__main_window = main_window
        self.__video_stream = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # capture video stream, '0' is default camera
        self.__video_stream.set(cv2.CAP_PROP_FRAME_WIDTH, 960)  # set video resolution to 800×600 or 960×720
        self.__video_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # default resolution is 640×480
        # Create tk.Frame container in GUI and make it expandable
        self.container = tk.Frame(self.__main_window.gui)
        self.container.pack(fill=tk.BOTH, expand=1)
        # Configure the rows and columns to have a non-zero weight so that they will take up the extra space
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)
        self.__panel = tk.Label(self.container, text='Web camera image', anchor='center')  # initialize image panel
        self.__panel.grid(row=0, column=0, sticky='nswe')  # make tk.Label expandable
        #
        self.__video_loop()  # start a video loop

    def add_buttons(self):
        """ Add buttons to the bottom of the GUI window """
        buttons = tk.Label(self.container)  # initialize buttons panel
        buttons.grid(row=1, column=0)
        tk.Button(buttons, text=self.__main_window._shortcuts['prev'][0],
                  command=self.__main_window._shortcuts['prev'][3]).pack(side=tk.LEFT)
        tk.Button(buttons, text=self.__main_window._shortcuts['save'][0],
                  command=self.__main_window._shortcuts['save'][3]).pack(side=tk.LEFT)
        tk.Button(buttons, text=self.__main_window._shortcuts['next'][0],
                  command=self.__main_window._shortcuts['next'][3]).pack(side=tk.LEFT)

    def __video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.__video_stream.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            if self.__main_window.extractor.image is not None:
                frame = self.__main_window.extractor.tracking(frame)
            frame = self.__resize_image(frame)  # resize frame for the GUI window
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert from BGR to RGBA
            image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=image)  # convert image for tkinter
            self.__panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.__panel.config(image=imgtk)  # show the image
        # Try to not set 1 ms or less than 10 ms, because the app will lag.
        self.__panel.after(20, self.__video_loop)  # call the same function after 20 milliseconds

    def __resize_image(self, image):
        """ Resize image proportionally """
        h1, w1 = image.shape[:2]  # color image has shape [h, w, 3]
        w1, h1 = float(w1), float(h1)
        w2, h2 = float(self.__panel.winfo_width()), float(self.__panel.winfo_height())
        aspect_ratio1 = w1 / h1
        aspect_ratio2 = w2 / h2
        if aspect_ratio1 == aspect_ratio2:
            shape = (int(w2), int(h2))
        elif aspect_ratio1 > aspect_ratio2:
            shape = (int(w2), max(1, int(w2 / aspect_ratio1)))
        else:  # aspect_ratio1 < aspect_ratio2
            shape = (max(1, int(h2 * aspect_ratio1)), int(h2))
        # Interpolation could be: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
        return cv2.resize(image, shape, interpolation=Image.ANTIALIAS)

    def get_snapshot(self):
        """ Take a new snapshot. Save it to the file. Pass the name of the new file to the application """
        uid = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')  # unique ID from the current timestamp
        filename = f'{uid}.png'  # construct filename from the UID
        filepath = os.path.join(self.__main_window.config.config_dir, filename)  # construct output path
        logging.info(f'Take a new snapshot: {filepath}')
        _, frame = self.__video_stream.read()  # read frame from video stream
        cv2.imwrite(filepath, frame)  # save image frame
        self.__main_window.set_image(filepath)  # close previous image and set a new one

    def destroy(self):
        """ Release all resources """
        self.__video_stream.release()  # release web camera
        cv2.destroyAllWindows()  # destroy all cv2 windows
