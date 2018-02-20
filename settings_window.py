# -*- coding: utf-8 -*-
# Settings / configure window for bigger project
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

class MainGUI(ttk.Frame):
    ''' Main GUI window '''
    def __init__(self, master):
        ''' Init main window '''
        ttk.Frame.__init__(self, master=master)
        self.master.title('Main GUI')
        self.master.geometry('300x200')
        ttk.Button(self.master, text='Settings', command=self.open_settings).pack()

    def open_settings(self):
        ''' Open settings modal window '''
        s = Settings(self.master)  # create settings object
        self.master.wait_window(s)  # display the settings window and wait for it to close

class Settings(simpledialog.Dialog):
    ''' Settings / configure window for bigger project '''
    def __init__(self, parent):
        ''' Init settings window '''
        tk.Toplevel.__init__(self, master=parent)
        self.create_settings_window()
        self.create_widgets()

    def create_settings_window(self):
        ''' Create setting window '''
        self.focus_set()  # set focus on the settings window
        self.grab_set()  # make a modal window, so all events go to settings window
        self.transient(self.master)  # show only one window in the task bar
        #
        self.title('Settings')  # set title
        # self.cancel gets fired when the window is destroyed
        self.protocol('WM_DELETE_WINDOW', self.cancel)
        # Set proper settings position over the parent window
        self.geometry('+{x}+{y}'.format(x = self.master.winfo_rootx() + 50,
                                        y = self.master.winfo_rooty() + 50))
        self.bind("<Escape>", self.cancel)  # close when <Escape> key is pressed

    def create_widgets(self):
        ''' Widgets for settings window are created here '''
        body = ttk.Frame(self)  # body frame with settings
        # place listbox here
        body.pack()
        #
        buttonbox = ttk.Frame(self)  # frame for 3 buttons: apply, ok and cancel
        ttk.Button(buttonbox, text='Apply', command=self.apply).pack(side='left', padx=5, pady=5)
        ttk.Button(buttonbox, text='Ok', command=self.ok).pack(side='left', padx=5, pady=5)
        ttk.Button(buttonbox, text='Cancel', command=self.cancel).pack(side='left', padx=5, pady=5)
        buttonbox.pack(side='right')

    def apply(self):
        ''' Apply settings changes '''
        pass

    def ok(self, event=None):
        ''' Apply changes and close settings window '''
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        ''' Close settings window '''
        self.master.focus_set()  # put focus back to the parent window
        self.destroy()  # destroy settings window

root = tk.Tk()
feedback = MainGUI(root)
root.mainloop()
