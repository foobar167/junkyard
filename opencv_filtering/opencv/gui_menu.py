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
        self.menubar.add_cascade(label='File', menu=file)  # add 'File' menu to menu bar
        s = shortcuts['next']  # next filter
        file.add_command(label=s[0], command=s[1], accelerator=s[2])
        s = shortcuts['last']  # last filter
        file.add_command(label=s[0], command=s[1], accelerator=s[2])
        s = shortcuts['save']  # save snapshot
        file.add_command(label=s[0], command=s[1], accelerator=s[2])
        file.add_separator()
        s = shortcuts['exit']  # exit program
        file.add_command(label=s[0], command=s[1], accelerator=s[2])
        # Create 'Filters' menu
        self.current_filter = tk.IntVar()
        s = shortcuts['filters']  # filters object
        filters = tk.Menu(self.menubar, tearoff=False, postcommand=lambda f=s[1]: self.get_filter(f))
        self.menubar.add_cascade(label=s[0], menu=filters)  # add 'Filters' menu to menu bar
        filter_names = s[1].get_names()  # get list of filter names
        for i, name in enumerate(filter_names):  # show list of filter names
            filters.add_radiobutton(label=name, value=i, variable=self.current_filter,
                                    command=lambda f=s[1]: self.set_filter(f))
        # Create 'Camera' menu
        self.current_camera = tk.IntVar()
        s = shortcuts['camera']  # camera object
        camera = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label=s[0], menu=camera)  # add 'Camera' menu to menu bar
        cameras_list = tk.Menu(camera, tearoff=False, postcommand=lambda c=s[1]: self.get_camera(c))
        camera.add_cascade(label='Cameras List', menu=cameras_list)  # add 'Cameras List' to 'Camera' menu
        for i in range(s[1].cameras_number):  # get cameras number
            cameras_list.add_radiobutton(label='Camera ' + str(i + 1), value=i, variable=self.current_camera,
                                         command=lambda c=s[1]: self.set_camera(c))
        #
        self.current_resolution = tk.IntVar()
        self.resolutions = tk.Menu(camera, tearoff=False, postcommand=lambda c=s[1]: self.get_resolutions(c))
        camera.add_cascade(label='Resolutions', menu=self.resolutions)  # add 'Resolutions' to 'Camera' menu
        # camera.add_command(label='Get Resolutions', command=s[1].available_resolutions)
        # Create 'View' menu
        view = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label='View', menu=view)  # add 'View' menu to menu bar
        s = shortcuts['fullscreen']
        view.add_command(label=s[0], command=s[1], accelerator=s[2])
        s = shortcuts['default']
        view.add_command(label=s[0], command=s[1], accelerator=s[2])

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
        cameras.set_camera(self.current_camera.get())  # change current camera

    def get_resolutions(self, cameras):
        """ Get list of available resolutions for the current web camera """
        resolutions_list = cameras.get_resolutions()  # get list of resolution names
        self.resolutions.delete(0, 'end')  # empty previous resolutions list
        for i, name in enumerate(resolutions_list):  # show list of resolutions
            self.resolutions.add_radiobutton(label=name, value=i, variable=self.current_resolution,
                                             command=lambda c=cameras: self.set_resolution(c))
        self.current_resolution.set(cameras.current_resolution)

    def set_resolution(self, cameras):
        """ Set resolution from the menu bar """
        cameras.set_resolution(self.current_resolution.get())  # change current resolution
