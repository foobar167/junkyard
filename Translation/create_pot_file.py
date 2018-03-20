# -*- coding: utf-8 -*-
# Create a POT file named multilanguage.pot. This is just a normal plain text file that
# lists all the translated strings it found in the source code by search for _() calls.
# Link: https://inventwithpython.com/blog/2014/12/20/translate-your-python-3-program-with-the-gettext-module
import os
import sys

# Get absolute path to pygettext.py file depending on path to the program being executed
path = os.path.abspath(os.path.join(sys.executable, os.pardir))  # get parent dir of sys.executable
path = os.path.join(path, 'Tools\\i18n\\pygettext.py')  # absolute path to pygettext.py file

# Find all Python files in the base directory and save them in the py_list variable
base_dir = os.path.dirname(sys.argv[0])  # get directory from filepath to this file
base_dir = os.path.join(base_dir, '.')  # go to land module directory
py_list = list(filter(lambda x: x.lower().endswith(u'.py'), os.listdir(base_dir)))
py_list = map(lambda x: os.path.join(base_dir, x), py_list)

# Create multilanguage.pot file from the list of Python files
# command = py -2.7 "c:\Python27\Tools\i18n\pygettext.py" -d "multilanguage" %list%
command = 'py -3.6 "' + path + '" -d "multilanguage" "' + '" "'.join(py_list) + '"'
os.system(command)
