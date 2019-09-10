# -*- coding: utf-8 -*-
import tkinter as tk


class Menu:
    """ Menu widget for the main GUI window """
    def __init__(self, master, shortcuts):
        """ Initialize the Menu """
        self.menubar = tk.Menu(master)  # create main menu bar
        self.empty_menu = tk.Menu(master)  # empty menu to hide the real menubar in fullscreen mode
        # Create 'File' menu
        file = tk.Menu(self.menubar, tearoff=False)
        file.add_command(label=shortcuts[0][0], command=shortcuts[0][1], accelerator=shortcuts[0][2])
        file.add_command(label=shortcuts[1][0], command=shortcuts[1][1], accelerator=shortcuts[1][2])
        file.add_command(label=shortcuts[2][0], command=shortcuts[2][1], accelerator=shortcuts[2][2])
        file.add_separator()
        file.add_command(label=shortcuts[3][0], command=shortcuts[3][1], accelerator=shortcuts[3][2])
        self.menubar.add_cascade(label='File', menu=file)
        # Create 'Filters' menu
        self.current_filter = tk.IntVar()
        filters = tk.Menu(self.menubar, tearoff=False,
                               postcommand=lambda f=shortcuts[4][1]: self.get_filter(f))
        self.menubar.add_cascade(label=shortcuts[4][0], menu=filters)
        filter_names = shortcuts[4][1].get_names()  # get list of filter names
        for i, name in enumerate(filter_names):  # show list of filter names
            filters.add_radiobutton(label=name, value=i, variable=self.current_filter,
                                    command=lambda f=shortcuts[4][1]: self.set_filter(f))
        self.current_filter.set(shortcuts[4][1].current_filter)  # set current filter to the menu bar
        # Create 'View' menu
        self.current_camera = tk.IntVar()
        view = tk.Menu(self.menubar, tearoff=False)
        cameras = tk.Menu(view, tearoff=False, postcommand=lambda c=shortcuts[5][1]: self.get_camera(c))
        for i in range(shortcuts[5][1].cameras_number):  # get cameras number
            cameras.add_radiobutton(label='Camera '+str(i+1), value=i, variable=self.current_camera,
                                    command=lambda c=shortcuts[5][1]: self.set_camera(c))
        view.add_cascade(label=shortcuts[5][0], menu=cameras)
        view.add_command(label=shortcuts[6][0], command=shortcuts[6][1], accelerator=shortcuts[6][2])
        view.add_command(label=shortcuts[7][0], command=shortcuts[7][1], accelerator=shortcuts[7][2])
        self.menubar.add_cascade(label='View', menu=view)

    def get_filter(self, filters):
        """ Get current filter and set it to the menu bar radio button """
        self.current_filter.set(filters.current_filter)

    def set_filter(self, filters):
        """ Set filter from the menu bar """
        filters.set_filter(self.current_filter.get())

    def get_camera(self, cameras):
        """ Get current camera and set it to the menu bar radio button """
        self.current_camera.set(cameras.current_camera)

    def set_camera(self, cameras):
        """ Set camera from the menu bar """
        cameras.set_camera(self.current_camera.get())
