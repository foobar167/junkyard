# Run file to start application
import os
import tkinter as tk

from extractor.logic_logger import init_logging, logging
from extractor.gui_main import MainGUI

if __name__ == '__main__':
    init_logging()
    logging.info('Start application')
    this_dir = os.path.dirname(os.path.realpath(__file__))  # path to this directory
    os.chdir(this_dir)  # make path to this dir the current path
    app = MainGUI()  # start the application
    app.gui.mainloop()  # application is up and running
    logging.info('Finish application')
