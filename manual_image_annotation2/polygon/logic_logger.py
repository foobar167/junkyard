# -*- coding: utf-8 -*-
import os
import sys
import logging

def init_logging():
    """ Initialize logging and write info both into logfile and console
        Usage example: land.logger.logging.info('Your message here')
        Logger levels: critical, error, warning, info, debug, notset """
    this_dir = os.path.dirname(os.path.realpath(__file__))  # path to this directory
    log_dir = os.path.join(this_dir, '..', 'temp')
    # Create logging directory if not exist
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    # specify logging configuration
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s, %(asctime)s, %(filename)s, %(funcName)s, %(message)s',
                        filename='{dir_name}/logfile.log'.format(dir_name=log_dir),
                        filemode='a')
    # define a handler which writes to the sys.stderr
    console = logging.StreamHandler()
    # set a format which is simpler for console usage
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    # Override sys.excepthook to log uncaught exceptions
    sys.excepthook = handle_uncaught_exception

def handle_uncaught_exception(errtype, value, traceback):
    """ Handle all uncaught exceptions """
    logger = logging.getLogger('')
    logger.error('Uncaught exception occured', exc_info=(errtype, value, traceback))

def handle_exception(exit_code = 0):
    """ Use: @land.logger.handle_exception(0)
        before every function which could cast an exception """
    def wrapper(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                logging.exception(error)
                if exit_code != 0:  # if zero, don't exit from the program
                    sys.exit(exit_code)  # exit from the program
        return inner
    return wrapper
