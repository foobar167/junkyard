# -*- coding: utf-8 -*-
# Settings window for bigger project

"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class MainWindow(tk.Frame):
    counter = 0
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.button = tk.Button(self, text="Create new window",
                                command=self.create_window)
        self.button.pack(side="top")

    def create_window(self):
        self.counter += 1
        t = tk.Toplevel(self)
        t.wm_title("Window #%s" % self.counter)
        l = tk.Label(t, text="This is window #%s" % self.counter)
        l.pack(side="top", fill="both", expand=True, padx=100, pady=100)

if __name__ == "__main__":
    root = tk.Tk()
    main = MainWindow(root)
    main.pack(side="top", fill="both", expand=True)
    root.mainloop()
"""

"""
from tkinter import *
import os
from tkinter import simpledialog

class Dialog(simpledialog.Dialog):
    def __init__(self, parent, title = None):
        Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent
        self.result = None
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        self.buttonbox()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.initial_focus.focus_set()
        self.wait_window(self)

    # construction hooks
    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden
        Label(master, text="First:").grid(row=0, sticky=W)
        Label(master, text="Second:").grid(row=1, sticky=W)
        self.e1 = Entry(master)
        self.e2 = Entry(master)
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.cb = Checkbutton(master, text="Hardcopy")
        self.cb.grid(row=2, columnspan=2, sticky=W)
        return self.e1  # initial focus

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = Frame(self)
        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    # standard button semantics
    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    # command hooks
    def validate(self):
        return 1 # override

    def apply(self):
        first = int(self.e1.get())
        second = int(self.e2.get())
        print(first, second)  # or something

root = Tk()
Button(root, text="Hello!").pack()
root.update()
d = Dialog(root)
root.mainloop()
"""

# -*- coding: utf-8 -*-
# Settings / configure window for bigger project
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

class MainGUI(ttk.Frame):
    ''' Main GUI window '''
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.master.title('Main GUI')
        self.master.geometry('300x200')
        ttk.Button(self.master, text='Settings', command=open_settings).pack()

def open_settings():
    settings = tk.Toplevel(master=root)  # build the settings window
    ttk.Button(settings, text='Close', command=settings.destroy).pack()
    settings.focus_set()  # set focus on the settings window
    settings.grab_set()  # make a modal window, all events go to it
    settings.transient(root)  # show only one window in the taskbar
    root.wait_window(settings) # display the settings and wait for it to close

root = tk.Tk()
feedback = MainGUI(root)
root.mainloop()
