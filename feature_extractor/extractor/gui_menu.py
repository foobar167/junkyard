import tkinter as tk


class Menu:
    """ Menu widget for the main GUI window """
    def __init__(self, master, config, shortcuts, functions):
        """ Initialize the Menu """
        self.__config = config  # obtain link on config file
        self.__shortcuts = shortcuts  # obtain link on keyboard shortcuts
        self.__func = functions  # obtain link on dictionary of functions
        self.menubar = tk.Menu(master)  # create main menu bar, public for the main GUI
        self.empty_menu = tk.Menu(master)  # empty menu to hide the real menubar in full screen mode
        # Enable / disable these menu labels
        self.__label_recent = 'Recent Images'
        self.__label_extractors = 'Extractors'
        # Create menu for the image
        self.__file = tk.Menu(self.menubar, tearoff=False, postcommand=self.__list_recent)
        self.__file.add_command(label='Open image',
                                command=self.__shortcuts[0][2],
                                accelerator=self.__shortcuts[0][0])
        self.__recent_images = tk.Menu(self.__file, tearoff=False)
        self.__file.add_cascade(label=self.__label_recent, menu=self.__recent_images)
        self.__file.add_separator()
        self.__file.add_command(label='Exit',
                                command=self.__func['destroy'],
                                accelerator=u'Alt+F4')
        self.menubar.add_cascade(label='File', menu=self.__file)
        # Create menu for the view: fullscreen, default size, etc.
        self.__view = tk.Menu(self.menubar, tearoff=False)
        self.__view.add_command(label='Fullscreen',
                                command=self.__func['toggle_fullscreen'],
                                accelerator='F11')
        self.__view.add_command(label='Default size',
                                command=self.__func['default_geometry'],
                                accelerator='F5')
        self.menubar.add_cascade(label='View', menu=self.__view)
        # Create menu for various feature extractors
        self.__extractors = tk.Menu(self.menubar, tearoff=False)
        self.__extractors.add_command(label='Test1',)
        self.__extractors.add_command(label='Test2',)
        self.__extractors.add_command(label='Test3',)
        self.menubar.add_cascade(label=self.__label_extractors, menu=self.__extractors, state='disabled')

    def __list_recent(self):
        """ List of the recent images """
        self.__recent_images.delete(0, 'end')  # empty previous list
        lst = self.__config.get_recent_list()  # get list of recently opened images
        for path in lst:  # get list of recent image paths
            self.__recent_images.add_command(label=path,
                                             command=lambda x=path: self.__func['set_image'](x))
        # Disable recent list menu if it is empty.
        if self.__recent_images.index('end') is None:
            self.__file.entryconfigure(self.__label_recent, state='disabled')
        else:
            self.__file.entryconfigure(self.__label_recent, state='normal')
