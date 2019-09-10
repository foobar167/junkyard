# -*- coding: utf-8 -*-
import cv2
import time

from tkinter import messagebox
from .logic_logger import logging


class MyValidationError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        logging.info(message)
        messagebox.showinfo(message, 'There are no web cameras on your computer.\nExit from the GUI.')


class Camera:
    """ Available web cameras """
    def __init__(self, current=0):
        """ Initialize object """
        self.cameras_number = self.count_cameras()
        if self.cameras_number == 0:  # check for the web camera
            raise MyValidationError('No web camera on the computer')
        self.current_camera = current  # current web camera
        # cv2.CAP_DSHOW is a flag DirectShow (via videoInput)
        self.camera = cv2.VideoCapture(self.current_camera, cv2.CAP_DSHOW)  # capture video frames

    @staticmethod
    def count_cameras():
        """ Get the number of cameras available """
        max_tested = 100  # maximum web cameras to test
        for i in range(max_tested):
            camera = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if camera.isOpened():
                camera.release()
                continue
            # BUG! If release camera too quickly there'll be a distorted image sometimes, but not always
            time.sleep(0.25)  # wait till the camera become ready
            return i

    def set_camera(self, number):
        """ Set current web camera """
        if self.current_camera != number:
            self.camera.release()  # release previously opened camera
            self.camera = cv2.VideoCapture(number, cv2.CAP_DSHOW)
            if self.camera.isOpened():  # ok
                self.current_camera = number
            else:  # keep old camera if something goes wrong
                self.camera = cv2.VideoCapture(self.current_camera, cv2.CAP_DSHOW)

    def read(self):
        """ Read frame from the video stream """
        return self.camera.read()

    def destroy(self):
        """ Destroy camera object """
        self.camera.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application
