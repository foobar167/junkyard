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
        self.driver = self.set_driver()  # set video driver
        self.cameras_number = self.available_cameras()  # get number of available cameras
        if self.cameras_number == 0:  # check for the web camera
            raise MyValidationError('No web camera on the computer')
        # List of common resolutions in the following format: [name, width, height]
        # Link: https://en.wikipedia.org/wiki/List_of_common_resolutions
        self.resolutions_all = [
            ['16×16', 16, 16],
            ['32×32', 32, 32],
            ['40×30', 40, 30],
            ['42×11', 42, 11],
            ['42×32', 42, 32],
            ['48×32', 48, 32],
            ['60×40', 60, 40],
            ['64×64', 64, 64],
            ['72×64', 72, 64],
            ['75×64', 75, 64],
            ['84×48', 84, 48],
            ['96×64', 96, 64],
            ['96×65', 96, 65],
            ['96×96', 96, 96],
            ['101×80', 101, 80],
            ['102×64', 102, 64],
            ['128×36', 128, 36],
            ['128×48', 128, 48],
            ['128×128', 128, 128],
            ['140×192', 140, 192],
            ['144×168', 144, 168],
            ['150×40', 150, 40],
            ['160×102', 160, 102],
            ['160×120', 160, 120],
            ['160×144', 160, 144],
            ['160×152', 160, 152],
            ['160×160', 160, 160],
            ['160×200', 160, 200],
            ['160×256', 160, 256],
            ['208×176', 208, 176],
            ['208×208', 208, 208],
            ['220×176', 220, 176],
            ['224×144', 224, 144],
            ['240×64', 240, 64],
            ['240×160', 240, 160],
            ['240×240', 240, 240],
            ['256×192', 256, 192],
            ['256×212', 256, 212],
            ['256×256', 256, 256],
            ['272×340', 272, 340],
            ['280×192', 280, 192],
            ['312×390', 312, 390],
            ['320×192', 320, 192],
            ['320×200', 320, 200],
            ['320×208', 320, 208],
            ['320×224', 320, 224],
            ['320×240', 320, 240],
            ['320×256', 320, 256],
            ['320×320', 320, 320],
            ['320×400', 320, 400],
            ['376×240', 376, 240],
            ['384×288', 384, 288],
            ['400×240', 400, 240],
            ['400×270', 400, 270],
            ['400×300', 400, 300],
            ['416×352', 416, 352],
            ['432×128', 432, 128],
            ['432×240', 432, 240],
            ['480×234', 480, 234],
            ['480×250', 480, 250],
            ['480×272', 480, 272],
            ['480×320', 480, 320],
            ['480×500', 480, 500],
            ['512×212', 512, 212],
            ['512×256', 512, 256],
            ['512×342', 512, 342],
            ['512×384', 512, 384],
            ['560×192', 560, 192],
            ['600×480', 600, 480],
            ['640×200', 640, 200],
            ['640×240', 640, 240],
            ['640×256', 640, 256],
            ['640×320', 640, 320],
            ['640×350', 640, 350],
            ['640×360', 640, 360],
            ['640×400', 640, 400],
            ['640×480', 640, 480],
            ['640×512', 640, 512],
            ['720×348', 720, 348],
            ['720×350', 720, 350],
            ['720×364', 720, 364],
            ['768×480', 768, 480],
            ['800×240', 800, 240],
            ['800×352', 800, 352],
            ['800×480', 800, 480],
            ['800×600', 800, 600],
            ['832×624', 832, 624],
            ['848×480', 848, 480],
            ['854×480', 854, 480],
            ['960×540', 960, 540],
            ['960×544', 960, 544],
            ['960×640', 960, 640],
            ['960×720', 960, 720],
            ['1024×576', 1024, 576],
            ['1024×600', 1024, 600],
            ['1024×640', 1024, 640],
            ['1024×768', 1024, 768],
            ['1024×800', 1024, 800],
            ['1024×1024', 1024, 1024],
            ['1080×1200', 1080, 1200],
            ['1120×832', 1120, 832],
            ['1136×640', 1136, 640],
            ['1152×720', 1152, 720],
            ['1152×768', 1152, 768],
            ['1152×864', 1152, 864],
            ['1152×900', 1152, 900],
            ['1280×720', 1280, 720],
            ['1280×768', 1280, 768],
            ['1280×800', 1280, 800],
            ['1280×854', 1280, 854],
            ['1280×960', 1280, 960],
            ['1280×1024', 1280, 1024],
            ['1334×750', 1334, 750],
            ['1366×768', 1366, 768],
            ['1400×1050', 1400, 1050],
            ['1440×900', 1440, 900],
            ['1440×960', 1440, 960],
            ['1440×1024', 1440, 1024],
            ['1440×1080', 1440, 1080],
            ['1440×1440', 1440, 1440],
            ['1600×768', 1600, 768],
            ['1600×900', 1600, 900],
            ['1600×1024', 1600, 1024],
            ['1600×1200', 1600, 1200],
            ['1600×1280', 1600, 1280],
            ['1680×1050', 1680, 1050],
            ['1776×1000', 1776, 1000],
            ['1792×1344', 1792, 1344],
            ['1800×1440', 1800, 1440],
            ['1856×1392', 1856, 1392],
            ['1920×1080', 1920, 1080],
            ['1920×1200', 1920, 1200],
            ['1920×1280', 1920, 1280],
            ['1920×1400', 1920, 1400],
            ['1920×1440', 1920, 1440],
            ['2048×1080', 2048, 1080],
            ['2048×1152', 2048, 1152],
            ['2048×1280', 2048, 1280],
            ['2048×1536', 2048, 1536],
            ['2160×1080', 2160, 1080],
            ['2160×1200', 2160, 1200],
            ['2160×1440', 2160, 1440],
            ['2256×1504', 2256, 1504],
            ['2280×1080', 2280, 1080],
            ['2304×1440', 2304, 1440],
            ['2304×1728', 2304, 1728],
            ['2436×1125', 2436, 1125],
            ['2538×1080', 2538, 1080],
            ['2560×1080', 2560, 1080],
            ['2560×1440', 2560, 1440],
            ['2560×1600', 2560, 1600],
            ['2560×1700', 2560, 1700],
            ['2560×1800', 2560, 1800],
            ['2560×1920', 2560, 1920],
            ['2560×2048', 2560, 2048],
            ['2732×2048', 2732, 2048],
            ['2736×1824', 2736, 1824],
            ['2800×2100', 2800, 2100],
            ['2880×900', 2880, 900],
            ['2880×1440', 2880, 1440],
            ['2880×1620', 2880, 1620],
            ['2880×1800', 2880, 1800],
            ['2960×1440', 2960, 1440],
            ['3000×2000', 3000, 2000],
            ['3200×1800', 3200, 1800],
            ['3200×2048', 3200, 2048],
            ['3200×2400', 3200, 2400],
            ['3240×2160', 3240, 2160],
            ['3440×1440', 3440, 1440],
            ['3840×1600', 3840, 1600],
            ['3840×2160', 3840, 2160],
            ['3840×2400', 3840, 2400],
            ['4096×2160', 4096, 2160],
            ['4096×3072', 4096, 3072],
            ['4500×3000', 4500, 3000],
            ['5120×2160', 5120, 2160],
            ['5120×2880', 5120, 2880],
            ['5120×3200', 5120, 3200],
            ['5120×4096', 5120, 4096],
            ['6400×4096', 6400, 4096],
            ['6400×4800', 6400, 4800],
            ['7680×4320', 7680, 4320],
            ['7680×4800', 7680, 4800],
            ['8192×4320', 8192, 4320],
            ['8192×4608', 8192, 4608],
            ['8192×8192', 8192, 8192],
            ['10240×4320', 10240, 4320],
            ['15360×8640', 15360, 8640],
        ]
        # Web camera resolutions - https://webcamtests.com/resolution
        self.resolutions_short = [
            ['160×120', 160, 120],
            ['176×144', 176, 144],
            ['192×144', 192, 144],
            ['240×160', 240, 160],
            ['320×240', 320, 240],
            ['352×240', 352, 240],
            ['352×288', 352, 288],
            ['384×288', 384, 288],
            ['480×360', 480, 360],
            ['640×360', 640, 360],
            ['640×480', 640, 480],
            ['704×480', 704, 480],
            ['720×480', 720, 480],
            ['800×480', 800, 480],
            ['800×600', 800, 600],
            ['960×720', 960, 720],
            ['1024×768', 1024, 768],
            ['1280×720', 1280, 720],
            ['1280×800', 1280, 800],
            ['1280×960', 1280, 960],
            ['1280×1024', 1280, 1024],
            ['1600×1200', 1600, 1200],
            ['1920×1080', 1920, 1080],
            ['2048×1536', 2048, 1536],
            ['2560×2048', 2560, 2048],
            ['3200×2400', 3200, 2400],
            ['4096×2160', 4096, 2160],
            ['4096×3072', 4096, 3072],
            ['5120×2160', 5120, 2160],
            ['5120×2880', 5120, 2880],
            ['5120×3200', 5120, 3200],
            ['5120×4096', 5120, 4096],
            ['6400×4096', 6400, 4096],
            ['6400×4800', 6400, 4800],
            ['7680×4320', 7680, 4320],
            ['7680×4800', 7680, 4800],
            ['10240×4320', 10240, 4320],
        ]
        # Hardcoded resolutions for Logitech camera, because it is too long to iterate through all of them
        resolutions_logitech = [
            ['Default', 0, 0],  # reserved for default resolution
            ['160×120', 160, 120],
            ['320×200', 320, 200],
            ['320×240', 320, 240],
            ['640×360', 640, 360],
            ['640×400', 640, 400],
            ['640×480', 640, 480],
            ['768×480', 768, 480],
            ['800×600', 800, 600],
            ['960×720', 960, 720],
            ['1280×720', 1280, 720],
            ['1280×800', 1280, 800],
            ['1280×1024', 1280, 1024],
            ['1600×900', 1600, 900],
            ['1600×1200', 1600, 1200],
            ['Maximum', 10000, 10000]
        ]
        self.camera_resolutions = resolutions_logitech
        self.current_camera = -1  # current camera is not set yet
        self.current_resolution = 0  # current resolution number in the list
        self.camera = None
        self.set_camera(current)

    @staticmethod
    def set_driver():
        """ Set available video driver """
        camera = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
        if camera.isOpened():
            camera.release()
            driver = cv2.CAP_DSHOW  # set DirectShow driver
        else:
            driver = 0  # set native driver
        cv2.destroyAllWindows()
        time.sleep(0.25)  # wait till the camera become ready
        return driver

    def available_cameras(self):
        """ Get the number of available cameras """
        max_tested = 10  # maximum web cameras to test
        for i in range(max_tested):
            camera = cv2.VideoCapture(i + self.driver)
            if camera.isOpened():
                camera.release()
                continue
            cv2.destroyAllWindows()
            # BUG! If release camera too quickly there'll be a distorted image sometimes, but not always
            time.sleep(0.25)  # wait till the camera become ready
            return i

    def set_camera(self, number):
        """ Set current web camera """
        if self.current_camera != number:
            if self.camera is not None:
                self.camera.release()  # release previously opened camera
            self.camera = cv2.VideoCapture(number + self.driver)
            if self.camera.isOpened():  # ok
                self.current_camera = number
            else:  # keep old camera if something goes wrong
                self.camera = cv2.VideoCapture(self.current_camera + self.driver)
            w = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.camera_resolutions[0] = ['Default ' + str(w) + '×' + str(h), w, h]
            self.current_resolution = 0

    def reopen_camera(self):
        """ Re-open camera """
        self.camera.release()  # release previously opened camera
        cv2.destroyAllWindows()
        self.camera = cv2.VideoCapture(self.current_camera + self.driver)

    def available_resolutions(self):
        """ Get list of available resolutions fot the current web camera.
            Brute force by looping over the list of common resolutions.
            It hang out for some cameras and very slow. """
        for res in self.resolutions_all:
            print(res)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,  res[1])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, res[2])
            if res[1] == int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)) and \
               res[2] == int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)):
                self.camera_resolutions.append(res)
            self.reopen_camera()  # BUG! Re-open camera after resolution reset.
        print('Number of resolutions:', len(self.camera_resolutions))
        print('List of resolutions:', self.camera_resolutions)

    def get_resolutions(self):
        """ Get list of resolutions for the current web camera """
        return [name[0] for name in self.camera_resolutions]

    def set_resolution(self, number):
        """ Set resolution from hardcoded camera resolutions list if possible """
        w = self.camera_resolutions[number][1]
        h = self.camera_resolutions[number][2]
        n = self.camera_resolutions[number][0]
        # Set resolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,  w)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        w2 = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        h2 = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        n2 = self.camera_resolutions[-1][0]
        # Check if resolution is set. It is not always happens
        if n == n2 or (w == w2 and h == h2):
            self.current_resolution = number  # change current resolution number

    def read(self):
        """ Read frame from the video stream """
        return self.camera.read()

    def destroy(self):
        """ Destroy camera object """
        self.camera.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application
