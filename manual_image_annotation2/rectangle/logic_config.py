# -*- coding: utf-8 -*-
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
        self.__opened_path = 'OpenedPath'  # last opened path of the task or image
        self.__default_opened_path = 'None'
        #
        self.__rectangle = 'RectangleWindow'  # info about the rolling window
        self.__rect_w = 'Width'  # width of rolling window
        self.__rect_h = 'Height'  # height of rolling window
        self.__default_rect_w, self.__default_rect_h = 320, 240  # default rolling window width/height
        #
        self.__recent = 'LastOpened'  # list of last opened paths
        self.__recent_number = 10  # number of recent paths
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

    def get_opened_path(self):
        """ Get opened path if it wasn't closed previously or return an empty string """
        try:
            path = self.__config[self.__window][self.__opened_path]
            if path == self.__default_opened_path or not os.path.exists(path):
                return ''
            else:
                return path
        except KeyError:  # if the key is not in the dictionary of config
            return ''

    def set_opened_path(self, path=None):
        """ Remember opened path to the config INI file """
        self.__check_section(self.__window)
        if path:
            self.__config[self.__window][self.__opened_path] = path
        else:
            self.__config[self.__window][self.__opened_path] = self.__default_opened_path

    def get_rect_size(self):
        """ Get tuple (width, height) of the rolling window """
        try:
            w = self.__config[self.__rectangle][self.__rect_w]
            h = self.__config[self.__rectangle][self.__rect_h]
            return int(w), int(h)
        except KeyError:  # if the key is not in the dictionary of config
            return self.__default_rect_w, self.__default_rect_h

    def set_rect_size(self, width=None, height=None):
        """ Set tuple (width, height) of the rolling window """
        self.__check_section(self.__rectangle)
        if width:
            self.__config[self.__rectangle][self.__rect_w] = str(width)
        else:
            self.__config[self.__rectangle][self.__rect_w] = str(self.__default_rect_w)
        if height:
            self.__config[self.__rectangle][self.__rect_h] = str(height)
        else:
            self.__config[self.__rectangle][self.__rect_h] = str(self.__default_rect_h)

    def get_recent_list(self):
        """ Get list of recently opened image paths """
        try:
            lst = self.__config.items(self.__recent)  # list of (key, value) pairs
            lst = [path for key, path in lst]  # leave only path
            for n, path in enumerate(lst):
                if not os.path.isfile(path):
                    del lst[n]  # delete non-existent file path from the list
            return lst
        except configparser.NoSectionError:  # no section with the list of last opened paths
            return ''

    def get_recent_path(self):
        """ Get last opened path from config INI file """
        try:
            path = self.__config[self.__recent]['1']
            path = os.path.abspath(os.path.join(path, os.pardir))  # get parent directory
            if not os.path.exists(path):
                return os.getcwd()  # return current directory
            return path
        except KeyError:  # if the key is not in the dictionary of config
            return os.getcwd()  # get current directory

    def set_recent_path(self, path):
        """ Set last opened path to config INI file """
        try:
            lst = self.__config.items(self.__recent)  # list of (key, value) pairs
        except configparser.NoSectionError:  # no section with the list of last opened paths
            lst = []  # there is no such section
        lst = [value for key, value in lst]  # leave only path
        if path in lst: lst.remove(path)  # delete path from list
        lst.insert(0, path)  # add path to the beginning of a list
        self.__config.remove_section(self.__recent)  # remove section
        self.__config.add_section(self.__recent)  # create empty section
        key = 1
        for name in lst:
            if os.path.exists(name):
                self.__config[self.__recent][str(key)] = name
                key += 1
            if key > self.__recent_number:
                break  # exit from the cycle

    def save(self):
        """ Save config file """
        with open(self.__config_path, 'w') as configfile:
            self.__config.write(configfile)

    def __new_config(self):
        """ Create new config INI file and put default values in it """
        self.set_win_geometry(self.default_geometry)
        self.set_win_state(self.default_state)
        self.set_rect_size()

    def destroy(self):
        """ Config destructor """
        self.save()
