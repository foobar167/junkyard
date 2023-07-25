import os
import configparser


class Config:
    """ This class is responsible for various operations with configuration INI file.
        ConfigParser module is a part of the standard Python library """
    def __init__(self, path='temp'):
        """ Initialize configure parameters for INI file """
        self.config_dir = path  # should be public for the main GUI
        self.__config_name = 'config.ini'  # name of config file
        self.__config_path = os.path.join(self.config_dir, self.__config_name)
        #
        # Value -- first place. Options -- second place.
        self.__window = 'Window'  # info about the main window
        self.__geometry = 'Geometry'  # size and position of the main window 'WxH±X±Y'
        self.default_geometry = '800x600+0+0'  # default window geometry 'WxH±X±Y'
        self.__state = 'State'  # state of the window: normal, zoomed, etc.
        self.default_state = 'normal'  # normal state of the window
        self.__default_opened_path = './data/book_cover.jpg'
        #
        self.__extractor = 'FeatureExtractor'  # info about feature extractor
        self.__name = 'Name'  # name of the last used feature extractor
        #
        self.__recent = 'LastOpened'  # list of last opened paths
        self.__recent_number = 10 + 1  # number of recent paths
        #
        self.__config = configparser.ConfigParser()  # create config parser
        self.__config.optionxform = lambda option: option  # preserve case for letters
        # Create config directory if not exist
        if not os.path.isdir(self.config_dir):
            os.makedirs(self.config_dir)
        # Create new config file if not exist or read existing one
        if not os.path.isfile(self.__config_path):
            self.__new_config()  # create new config
        else:
            self.__config.read(self.__config_path)  # read existing config file

    def __check_section(self, section):
        """ Check if section exists and create it if not """
        if not self.__config.has_section(section):
            self.__config.add_section(section)

    def get_win_geometry(self):
        """ Get main window size and position """
        try:
            return self.__config[self.__window][self.__geometry]
        except KeyError:  # if the key is not in the dictionary of config
            return self.default_geometry

    def set_win_geometry(self, geometry):
        """ Set main window size """
        self.__check_section(self.__window)
        self.__config[self.__window][self.__geometry] = geometry

    def get_win_state(self):
        """ Get main window state: normal, zoomed, etc. """
        try:
            return self.__config[self.__window][self.__state]
        except KeyError:  # if the key is not in the dictionary of config
            return self.default_state

    def set_win_state(self, state):
        """ Set main window state: normal, zoomed, etc. """
        self.__check_section(self.__window)
        self.__config[self.__window][self.__state] = state

    def get_extractor_name(self):
        """ Get the name of the last used feature extractor """
        try:
            return self.__config[self.__extractor][self.__name]
        except KeyError:  # if the key
            return None

    def set_extractor_name(self, name):
        """ Save the name of the last used feature extractor """
        self.__check_section(self.__extractor)
        self.__config[self.__extractor][self.__name] = name

    def get_recent_image(self):
        """ Get recently opened image or return a None """
        try:
            path = self.__config[self.__recent]['1']
            if os.path.isfile(path):
                return path
            else:
                return None
        except KeyError:  # if the key is not in the dictionary of config
            return None

    def set_recent_image(self, path):
        """ Set last opened path to config INI file """
        self.__check_section(self.__recent)
        lst = self.__config.items(self.__recent)  # list of (key, value) pairs
        lst = [value for key, value in lst]  # leave only path
        if path in lst:
            lst.remove(path)  # delete path from a list
        lst.insert(0, path)  # add path to the beginning of a list
        self.__config.remove_section(self.__recent)  # remove section
        self.__config.add_section(self.__recent)  # create empty section
        key = 1
        for name in lst:
            if os.path.isfile(name):
                self.__config[self.__recent][str(key)] = name
                key += 1
            if key > self.__recent_number:
                break  # exit from the cycle

    def get_recent_dir(self):
        """ Get last opened path from config INI file """
        path = self.get_recent_image()
        if path is not None:
            return os.path.abspath(os.path.join(path, os.pardir))  # get parent directory
        else:
            return os.getcwd()  # return current directory

    def get_recent_list(self, del_first=True):
        """ Get list of recently opened image paths """
        try:
            lst = self.__config.items(self.__recent)  # list of (key, value) pairs
            lst = [path for key, path in lst]  # leave only path
            if del_first:
                lst = lst[1:]  # delete first path, because it is already in use
            for n, path in enumerate(lst):
                if not os.path.isfile(path):
                    del lst[n]  # delete non-existent file path from the list
            return lst
        except configparser.NoSectionError:  # no section with the list of last opened paths
            return []

    def __set_recent_list(self):
        """ Set recently opened image paths to INI config file """
        self.__check_section(self.__recent)
        lst = self.get_recent_list(del_first=False)
        self.__config.remove_section(self.__recent)  # remove section
        self.__config.add_section(self.__recent)  # create empty section
        key = 1
        for name in lst:
            if os.path.isfile(name):
                self.__config[self.__recent][str(key)] = name  # add file to section
                key += 1

    def __new_config(self):
        """ Create new config INI file and put default values in it """
        self.set_win_geometry(self.default_geometry)
        self.set_win_state(self.default_state)
        self.set_recent_image(self.__default_opened_path)

    def destroy(self):
        """ Config destructor """
        self.__set_recent_list()  # exclude non-existing file paths from the list
        with open(self.__config_path, 'w') as configfile:
            self.__config.write(configfile)  # save config file
