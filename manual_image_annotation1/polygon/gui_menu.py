# -*- coding: utf-8 -*-
import tkinter as tk

class Menu:
    """ Menu widget for the main GUI window """
    def __init__(self, master, config, shortcuts, functions):
        """ Initialize the Menu """
        self.__config = config  # obtain link on config file
        self.__shortcuts = shortcuts  # obtain link on keyboard shortcuts
        self.__functs = functions  # obtain link on dictionary of functions
        self.menubar = tk.Menu(master)  # create main menu bar, public for the main GUI
        self.empty_menu = tk.Menu(master)  # empty menu to hide the real menubar in fullscreen mode
        # Enable / disable these menu labels
        self.__label_recent = 'Open recent'
        self.__label_close = 'Close image'
        self.__label_tools = 'Tools'
        self.__label_roll = 'Rolling Window'
        self.__label_poly_roi = 'Draw ROI'
        self.__label_poly_hole = 'Draw holes'
        self.__label_poly = self.__label_poly_hole
        self.__label_open = 'Open polygons'
        self.__label_save = 'Save polygons'
        self.__label_show_rect = 'Show Rect'
        self.__label_hide_rect = 'Hide Rect'
        self.__label_rect = self.__label_show_rect
        # Create menu for the image
        self.__file = tk.Menu(self.menubar, tearoff=False, postcommand=self.__list_recent)
        self.__file.add_command(label='Open image',
                              command=self.__shortcuts[0][2],
                              accelerator=self.__shortcuts[0][0])
        self.__recent_images = tk.Menu(self.__file, tearoff=False)
        self.__file.add_cascade(label=self.__label_recent, menu=self.__recent_images)
        self.__file.add_command(label=self.__label_close,
                              command=self.__shortcuts[1][2],
                              accelerator=self.__shortcuts[1][0],
                              state='disabled')
        self.__file.add_separator()
        self.__file.add_command(label='Exit',
                              command=self.__functs['destroy'],
                              accelerator=u'Alt+F4')
        self.menubar.add_cascade(label='File', menu=self.__file)
        # Create menu for the tools: cut rectangular images with the rolling window, etc.
        self.__tools = tk.Menu(self.menubar, tearoff=False, postcommand=self.__check_polygons)
        self.__tools.add_command(label=self.__label_roll,
                                 command=self.__shortcuts[2][2],
                                 accelerator=self.__shortcuts[2][0],
                                 state='disabled')
        self.__tools.add_separator()
        self.__tools.add_command(label=self.__label_poly,
                                 command=self.__shortcuts[3][2],
                                 accelerator=self.__shortcuts[3][0])
        self.__tools.add_separator()
        self.__tools.add_command(label=self.__label_open,
                                 command=self.__shortcuts[4][2],
                                 accelerator=self.__shortcuts[4][0])
        self.__tools.add_command(label=self.__label_save,
                                 command=self.__shortcuts[5][2],
                                 accelerator=self.__shortcuts[5][0])
        self.menubar.add_cascade(label=self.__label_tools, menu=self.__tools, state='disabled')
        # Create menu for the view: fullscreen, default size, etc.
        self.__view = tk.Menu(self.menubar, tearoff=False)
        self.__view.add_command(label='Fullscreen',
                                command=self.__functs["toggle_fullscreen"],
                                accelerator='F11')
        self.__view.add_command(label='Default size',
                                command=self.__functs["default_geometry"],
                                accelerator='F5')
        self.__view.add_command(label=self.__label_rect,
                                command=self.__shortcuts[6][2],
                                accelerator=self.__shortcuts[6][0])
        self.menubar.add_cascade(label='View', menu=self.__view)

    def __list_recent(self):
        """ List of the recent images """
        self.__recent_images.delete(0, 'end')  # empty previous list
        lst = self.__config.get_recent_list()  # get list of recently opened images
        for path in lst:  # get list of recent image paths
            self.__recent_images.add_command(label=path,
                                             command=lambda x=path: self.__functs["set_image"](x))
        # Disable recent list menu if it is empty.
        if self.__recent_images.index('end') is None:
            self.__file.entryconfigure(self.__label_recent, state='disabled')
        else:
            self.__file.entryconfigure(self.__label_recent, state='normal')

    def __check_polygons(self):
        """ Check if there are polygons on the image and enable/disable menu 'Rolling Window' """
        if self.__functs["check_roi"]():  # there are regions of interest on the image
            self.__tools.entryconfigure(self.__label_roll, state='normal')  # enable menu
        else:  # if there are no polygons
            self.__tools.entryconfigure(self.__label_roll, state='disabled')  # disable menu

    def set_state(self, state, roi=False, rect=None):
        """ Enable / disable some menus """
        self.menubar.entryconfigure(self.__label_tools, state=state)
        self.__file.entryconfigure(self.__label_close, state=state)
        self.__view.entryconfigure(self.__label_rect, state=state)
        self.set_tools_toggle(roi)
        self.show_rect(rect)

    def set_tools_toggle(self, roi):
        """ Change label of the toggle submenu 'Draw ROI/holes' of 'Tools' menu """
        label = self.__label_poly_hole if roi else self.__label_poly_roi
        self.__tools.entryconfigure(self.__label_poly, label=label)  # change menu text
        self.__label_poly = label  # update menu label to find it next time

    def show_rect(self, rect=False):
        """ Change label of the 'Show / Hide Rect' submenu """
        label = self.__label_hide_rect if rect else self.__label_show_rect
        self.__view.entryconfigure(self.__label_rect, label=label)  # change menu text
        self.__label_rect = label  # update menu label to find it next time
