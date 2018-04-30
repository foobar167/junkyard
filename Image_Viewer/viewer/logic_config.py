# -*- coding: utf-8 -*-
import os
import configparser

class Config():
    """ This class is responsible for various operations with configuration INI file.
        ConfigParser module is a part of the standard Python library """
    def __init__(self, path='temp'):
        """ Initialize configure parameters for INI file """
        self.__config_name = 'config.ini'  # name of config file
        self.__config_path = os.path.join(path, self.__config_name)
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
        self.__roi = 'Roi'  # info about the scanning window (region of interest)
        self.__roi_width = 'Width'  # width of scanning window
        self.__roi_height = 'Height'  # height of scanning window
        self.__default_roi_w, self.__default_roi_h = 320, 240  # default roi width / height
        #
        self.__recent = 'LastOpened'  # list of last opened paths
        self.__recent_number = 10  # number of recent paths
        #
        self.__config = configparser.ConfigParser()  # create config parser
        self.__config.optionxform = lambda option: option  # preserve case for letters
        # Create config directory if not exist
        if not os.path.isdir(path):
            os.makedirs(path)
        # Create new config file if not exist or read existing one
        if not os.path.isfile(self.__config_path):
            self.__new_config()
        else:
            self.__config.read(self.__config_path)

    def __check_section(self, section):
        """ Check if section exists and create it if not """
        if not self.__config[section]:
            self.__config[section] = {}

    def get_win_geometry(self):
        """ Get main window size and position """
        try:
            return self.__config[self.__window][self.__geometry]
        except:
            return self.default_geometry

    def set_win_geometry(self, geometry):
        """ Set main window size """
        self.__check_section(self.__window)
        self.__config[self.__window][self.__geometry] = geometry

    def get_win_state(self):
        """ Get main window state: normal, zoomed, etc. """
        try:
            return self.__config[self.__window][self.__state]
        except:
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
        except:
            return ''

    def set_opened_path(self, path = ''):
        """ Remember opened path to the config INI file """
        self.__check_section(self.__window)
        if path:
            self.__config[self.__window][self.__opened_path] = path
        else:
            self.__config[self.__window][self.__opened_path] = self.__default_opened_path

    def get_roi_size(self):
        """ Get tuple (width, height) of the roi window """
        try:
            w = self.__config[self.__roi][self.__roi_width]
            h = self.__config[self.__roi][self.__roi_height]
            return int(w), int(h)
        except:
            return self.__default_roi_w, self.__default_roi_h

    def set_roi_size(self, width=None, height=None):
        """ Set tuple (width, height) of the roi window """
        self.__check_section(self.__roi)
        if width:
            self.__config[self.__roi][self.__roi_width] = width
        else:
            self.__config[self.__roi][self.__roi_width] = self.__default_roi_w
        if height:
            self.__config[self.__roi][self.__roi_height] = height
        else:
            self.__config[self.__roi][self.__roi_height] = self.__default_roi_h

    def get_recent_list(self):
        """ Get list of recently opened image paths """
        try:
            l = self.__config.items(self.__recent)  # list of (key, value) pairs
            l = [path for key, path in l]  # leave only path
            for n, path in enumerate(l):
                if not os.path.isfile(path):
                    del l[n]  # delete non-existent file path from the list
            return l
        except:
            return ''

    def get_recent_path(self):
        ''' Get last opened path from config INI file '''
        try:
            path = self.__config[self.__recent]['1']
            path = os.path.abspath(os.path.join(path, os.pardir))  # get parent directory
            if not os.path.exists(path):
                return os.getcwdu()  # return current directory
            return path
        except:
            return os.getcwdu()  # get current directory (in unicode)

    def set_recent_path(self, path):
        """ Set last opened path to config INI file """
        try:
            l = self.__config.items(self.__recent)  # list of (key, value) pairs
        except:
            l = []  # there is no such section
        l = [value for key, value in l]  # leave only path
        if path in l: l.remove(path)  # delete path from list
        l.insert(0, path)  # add path to the beginning of a list
        self.__config.remove_section(self.__recent)  # remove section
        self.__config.add_section(self.__recent)  # create empty section
        key = 1
        for name in l:
            if os.path.exists(name):
                self.__config[self.__recent][key] = name
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
        self.set_roi_size()

    def destroy(self):
        """ Config destructor """
        self.save()
