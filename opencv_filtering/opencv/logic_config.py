# -*- coding: utf-8 -*-
import os
import cv2
import configparser


class Config:
    """ This class is responsible for various operations with configuration INI file.
        ConfigParser module is a part of the standard Python library """
    def __init__(self, path='temp'):
        """ Initialize configure parameters for INI file """
        self.__config_dir = path
        self.__config_name = 'config.ini'  # name of config file
        self.__config_path = os.path.join(self.__config_dir, self.__config_name)
        #
        # Value -- first place. Options -- second place.
        self.__window = 'Window'  # info about the main window
        self.__geometry = 'Geometry'  # size and position of the main window 'WxH±X±Y'
        self.default_geometry = '644x510+0+0'  # default window geometry 'Width x Height ± X ± Y'
        self.__state = 'State'  # state of the window: normal, zoomed, etc.
        self.default_state = 'normal'  # normal state of the window
        self.__current_camera = 'CurrentCamera'  # current web camera
        self.__default_camera = '0'  # default current camera number
        #
        self.__filter = 'Filter'  # info about filter
        self.__current_filter = 'CurrentFilter'  # current filter number
        self.__default_filter = '0'  # default current filter number
        #
        self.__config = configparser.ConfigParser()  # create config parser
        self.__config.optionxform = lambda option: option  # preserve case for letters
        # Create config directory if not exist
        if not os.path.isdir(self.__config_dir):
            os.makedirs(self.__config_dir)
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

    def get_current_camera(self):
        """ Get current camera if it is available or return default camera """
        try:
            current_camera = self.__config[self.__window][self.__current_camera]
            # Check current camera is available
            camera = cv2.VideoCapture(current_camera, cv2.CAP_DSHOW)
            if camera.isOpened():
                camera.release()
                return int(current_camera)
            else:
                return int(self.__default_camera)
        except KeyError:  # if the key is not in the dictionary of config
            return int(self.__default_camera)

    def set_current_camera(self, current_camera=None):
        """ Set current camera to the config INI file """
        self.__check_section(self.__window)
        if current_camera is None:
            current_camera = self.__default_camera
        self.__config[self.__window][self.__current_camera] = str(current_camera)

    def get_current_filter(self):
        """ Get current filter if it is available or return default filter """
        try:
            current_filter = self.__config[self.__filter][self.__current_filter]
            return int(current_filter)
        except KeyError:  # if the key is not in the dictionary of config
            return int(self.__default_filter)

    def set_current_filter(self, current_filter=None):
        """ Set current filter to the config INI file """
        self.__check_section(self.__filter)
        if current_filter is None:
            current_filter = self.__default_filter
        self.__config[self.__filter][self.__current_filter] = str(current_filter)

    def save(self):
        """ Save config file """
        with open(self.__config_path, 'w') as configfile:
            self.__config.write(configfile)

    def __new_config(self):
        """ Create new config INI file and put default values in it """
        self.set_win_geometry(self.default_geometry)
        self.set_win_state(self.default_state)

    def destroy(self):
        """ Config destructor """
        self.save()
