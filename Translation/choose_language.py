#
# Link: https://inventwithpython.com/blog/2014/12/20/translate-your-python-3-program-with-the-gettext-module
#
import sys
import os
import gettext
import tkinter as tk
from tkinter import ttk

def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, * sys.argv)

def change_language():
    global _
    if _('Hello world!') == 'Hello world!':
        del(_)
        ru = gettext.translation('choose_language', localedir='locale', languages=['ru'])
        ru.install()
    else:
        _ = lambda s: s
    print(_('Hello world!'))
    print(_('What is your name?'))

root = tk.Tk()
root.geometry('200x150+0+0')
_ = lambda s: s
ttk.Button(text='Change language', command=change_language).pack()
root.mainloop()
