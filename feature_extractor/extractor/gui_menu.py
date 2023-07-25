import tkinter as tk

from .logic_extractor import FeatureExtractor


class Menu:
    """ Menu widget for the main GUI window """
    def __init__(self, main_window):
        """ Initialize the Menu """
        self.__main_window = main_window
        self.menubar = tk.Menu(self.__main_window.gui)  # create main menu bar, public for the main GUI
        self.empty_menu = tk.Menu(self.__main_window.gui)  # empty menu to hide the real menubar in full screen mode
        # Enable / disable these menu labels
        self.__label_recent = 'Recent Images'
        self.__label_extractors = 'Extractors'
        self.__file, self.__recent_images, self.__view = None, None, None
        self.current_extractor, self.__extractors_list, self.__extractors = None, None, None

    def create_menu(self):
        """ Create menu bars """
        # Create menu 'File'
        self.__file = tk.Menu(self.menubar, tearoff=False, postcommand=self.__recent_list)
        self.__file.add_command(label=self.__main_window._shortcuts['open'][0],
                                command=self.__main_window._shortcuts['open'][3],
                                accelerator=self.__main_window._shortcuts['open'][1])
        self.__recent_images = tk.Menu(self.__file, tearoff=False)
        self.__file.add_cascade(label=self.__label_recent, menu=self.__recent_images)
        self.__file.add_separator()
        self.__file.add_command(label='Exit',
                                command=self.__main_window.destroy,
                                accelerator=u'Alt+F4')
        self.menubar.add_cascade(label='File', menu=self.__file)
        # Create menu 'View' (fullscreen, default size, etc.)
        self.__view = tk.Menu(self.menubar, tearoff=False)
        self.__view.add_command(label='Fullscreen',
                                command=self.__main_window._toggle_fullscreen,
                                accelerator='F11')
        self.__view.add_command(label='Default size',
                                command=self.__main_window._default_geometry,
                                accelerator='F5')
        self.menubar.add_cascade(label='View', menu=self.__view)
        # Create menu 'Extractors'
        self.current_extractor = tk.IntVar()
        self.__extractors_list = FeatureExtractor.__subclasses__()  # list of all subclasses of the abstract class
        self.__extractors = tk.Menu(self.menubar, tearoff=False, postcommand=self.__toggle_extractors)
        for i, e in enumerate(self.__extractors_list):  # add list of extractors to the menu
            name = str(e.name)  # name of extractor
            if name == self.__main_window.extractor.name:
                self.current_extractor.set(i)  # set current extractor to the menu bar radio button
            self.__extractors.add_radiobutton(
                label=name, value=i, variable=self.current_extractor,
                command=lambda n=i: self.set_extractor(n))
        self.menubar.add_cascade(label=self.__label_extractors, menu=self.__extractors)
        self.__toggle_extractors()  # enable / disable extractors menu

    def __recent_list(self):
        """ List of the recent images """
        self.__recent_images.delete(0, 'end')  # empty previous list
        lst = self.__main_window.config.get_recent_list()  # get list of recently opened images
        for path in lst:  # get list of recent image paths
            self.__recent_images.add_command(label=path,
                                             command=lambda x=path: self.__main_window.set_image(x))
        # Disable recent list menu if it is empty
        if self.__recent_images.index('end') is None:
            self.__file.entryconfigure(self.__label_recent, state='disabled')
        else:
            self.__file.entryconfigure(self.__label_recent, state='normal')

    def __toggle_extractors(self):
        """ Enable / disable list of extractors in the menu """
        # Disable if the list of extractors is empty or if image to track is not set
        if self.__extractors.index('end') is None or self.__main_window.extractor.image is None:
            self.menubar.entryconfigure(self.__label_extractors, state='disabled')
        else:
            self.menubar.entryconfigure(self.__label_extractors, state='normal')

    def set_extractor(self, number):
        """ Set new current feature extractor """
        name = self.__extractors_list[number].name
        config = self.__main_window.config
        #
        self.current_extractor.set(number)  # set current extractor to the menu bar radio button
        self.__main_window.extractor = self.__extractors_list[number](config.get_recent_image())
        config.set_extractor_name(name)  # save name in config file
        self.__main_window.gui.title(self.__main_window.default_title + ': ' + name)  # set window title

    def next_extractor(self):
        """ Set next extractor in a row """
        index = (self.current_extractor.get() + 1) % len(self.__extractors_list)
        self.set_extractor(index)

    def prev_extractor(self):
        """ Set previous extractor in a row """
        index = (self.current_extractor.get() - 1) % len(self.__extractors_list)
        self.set_extractor(index)
