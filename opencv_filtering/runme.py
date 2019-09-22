# -*- coding: utf-8 -*-
# Take snapshot using web camera, OpenCV and Tkinter.
import os
import tkinter as tk

from opencv.logic_logger import init_logging, logging
from opencv.gui_main import MainGUI
from opencv.logic_camera import MyValidationError


class TkErrorCatcher:
    """ Handle MyValidationError in the tkinter mainloop """
    def __init__(self, func, subst, widget):
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)
        except MyValidationError as err:  # handle MyValidationError in the mainloop
            raise err


tk.CallWrapper = TkErrorCatcher  # catch some validation errors

if __name__ == '__main__':
    init_logging()
    logging.info('Start software')
    this_dir = os.path.dirname(os.path.realpath(__file__))  # path to this directory
    os.chdir(this_dir)  # make path to this dir the current path
    try:
        app = MainGUI(tk.Tk())  # start the application
        app.mainloop()  # application is up and running
    except MyValidationError:
        pass
    finally:
        logging.info('Finish software')
