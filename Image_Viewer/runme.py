# -*- coding: utf-8 -*-
import os
import tkinter as tk

from viewer.logic_logger import init_logging, logging
from viewer.gui_main import MainGUI

if __name__ == '__main__':
    init_logging()
    logging.info('Start software')
    this_dir = os.path.dirname(os.path.realpath(__file__))  # path to this directory
    os.chdir(this_dir)  # make path to this dir the current path
    root = tk.Tk()
    app = MainGUI(root)
    root.mainloop()
    logging.info('Finish software')
