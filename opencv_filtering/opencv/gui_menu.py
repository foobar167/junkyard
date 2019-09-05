# -*- coding: utf-8 -*-
import tkinter as tk


class Menu:
    """ Menu widget for the main GUI window """
    def __init__(self, master, shortcuts):
        """ Initialize the Menu """
        self.menubar = tk.Menu(master)  # create main menu bar
        # Create 'File' menu
        self.file = tk.Menu(self.menubar, tearoff=False)
        self.file.add_command(label=shortcuts[0][0], command=shortcuts[0][1], accelerator=shortcuts[0][2])
        self.file.add_command(label=shortcuts[1][0], command=shortcuts[1][1], accelerator=shortcuts[1][2])
        self.file.add_command(label=shortcuts[2][0], command=shortcuts[2][1], accelerator=shortcuts[2][2])
        self.file.add_separator()
        self.file.add_command(label=shortcuts[3][0], command=shortcuts[3][1], accelerator=shortcuts[3][2])
        self.menubar.add_cascade(label='File', menu=self.file)
        # Create 'Filters' menu
        self.filters = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label='Filters', menu=self.filters, state='disabled')
