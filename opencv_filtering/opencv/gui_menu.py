# -*- coding: utf-8 -*-
import tkinter as tk


class Menu:
    """ Menu widget for the main GUI window """
    def __init__(self, master, shortcuts):
        """ Initialize the Menu """
        self.menubar = tk.Menu(master)  # create main menu bar
        self.empty_menu = tk.Menu(master)  # empty menu to hide the real menubar in fullscreen mode
        # Create 'File' menu
        self.file = tk.Menu(self.menubar, tearoff=False)
        self.file.add_command(label=shortcuts[0][0], command=shortcuts[0][1], accelerator=shortcuts[0][2])
        self.file.add_command(label=shortcuts[1][0], command=shortcuts[1][1], accelerator=shortcuts[1][2])
        self.file.add_command(label=shortcuts[2][0], command=shortcuts[2][1], accelerator=shortcuts[2][2])
        self.file.add_separator()
        self.file.add_command(label=shortcuts[3][0], command=shortcuts[3][1], accelerator=shortcuts[3][2])
        self.menubar.add_cascade(label='File', menu=self.file)
        # Create 'Filters' menu
        self.variable = tk.IntVar()
        self.filters = tk.Menu(self.menubar, tearoff=False,
                               postcommand=lambda f=shortcuts[4][1]: self.get_filter(f))
        self.menubar.add_cascade(label=shortcuts[4][0], menu=self.filters)
        filter_names = shortcuts[4][1].get_names()  # get list of filter names
        for i, name in enumerate(filter_names):  # show list of filter names
            self.filters.add_radiobutton(label=name, value=i, variable=self.variable,
                                         command=lambda f=shortcuts[4][1]: self.set_filter(f))
        self.variable.set(shortcuts[4][1].current_filter)  # set current filter to the menu bar
        # Create 'View' menu
        self.view = tk.Menu(self.menubar, tearoff=False)
        self.view.add_command(label=shortcuts[5][0], command=shortcuts[5][1], accelerator=shortcuts[5][2])
        self.view.add_command(label=shortcuts[6][0], command=shortcuts[6][1], accelerator=shortcuts[6][2])
        self.menubar.add_cascade(label='View', menu=self.view)

    def get_filter(self, filters):
        """ Get current filter and set it to the menu bar radio button """
        self.variable.set(filters.current_filter)

    def set_filter(self, filters):
        """ Set filter from the menu bar """
        filters.set_filter(self.variable.get())
