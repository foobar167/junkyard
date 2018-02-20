# -*- coding: utf-8 -*-
# Settings / configure window for bigger project
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

class AutoScrollbar(ttk.Scrollbar):
    ''' A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager '''
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError(u'Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError(u'Cannot use place with this widget')

class MainGUI(ttk.Frame):
    ''' Main GUI window '''
    def __init__(self, master):
        ''' Init main window '''
        ttk.Frame.__init__(self, master=master)
        self.master.title('Main GUI')
        self.master.geometry('300x200')
        self.list = ['one', 'two', 'three', 'four', 'five', 'very long interesting class name', 'six',
                     'seven', 'eight', 'nine', 'ten', 'eleven', 'ok?']
        ttk.Button(self.master, text='Settings', command=self.open_settings).pack()

    def open_settings(self):
        ''' Open settings modal window '''
        s = Settings(self.master, self.list)  # create settings object
        self.master.wait_window(s)  # display the settings window and wait for it to close

class Settings(simpledialog.Dialog):
    ''' Settings / configure window for bigger project '''
    def __init__(self, parent, list):
        ''' Init settings window '''
        tk.Toplevel.__init__(self, master=parent)
        self.list = list
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
        w = 12  # width of the buttons and entry
        one = ttk.Frame(self)  # upper frame with settings
        one.grid(row=0, column=0, sticky='w', pady=5)
        ttk.Label(one, text='Frame size:')       .pack(side='left')
        ttk.Entry(one, width=4, state='disabled').pack(side='left')
        ttk.Label(one, text='x')                 .pack(side='left')
        ttk.Entry(one, width=4, state='disabled').pack(side='left')
        #
        self.rowconfigure   (1, weight=1)  # make frame two extendable
        self.columnconfigure(0, weight=1)
        two = ttk.Frame(self)  # lower frame with settings
        two.rowconfigure   (0, weight=1)  # make ListBox extendable
        two.columnconfigure(0, weight=1)
        two.grid(row=1, column=0, sticky='nswe')
        # Vertical and horizontal scrollbars for ListBox
        vbar = AutoScrollbar(two, orient=u'vertical')
        hbar = AutoScrollbar(two, orient=u'horizontal')
        vbar.grid(row=0, column=1, sticky=u'ns')
        hbar.grid(row=1, column=0, sticky=u'we')
        # Create ListBox
        listbox = tk.Listbox(two, xscrollcommand=hbar.set, yscrollcommand=vbar.set,
                             selectmode='browse')  # browse == use only one selection at a time
        listbox.grid(row=0, column=0, sticky='nswe')
        hbar.configure(command=listbox.xview)  # bind scrollbars with ListBox
        vbar.configure(command=listbox.yview)
        #
        # Fill ListBox with data
        for classname in self.list:
            listbox.insert('end', classname)
        #
        right1 = ttk.Frame(two)  # right frame container for buttons and entry widget
        right1.grid(row=0, column=2, sticky='n')
        ttk.Entry (right1, width=w)               .grid(row=0, column=0, padx=5)
        ttk.Button(right1, width=w, text='Add')   .grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(right1, width=w, text='Remove').grid(row=2, column=0, padx=5)
        #
        right2 = ttk.Frame(two)  # right frame container for buttons
        right2.grid(row=0, column=2, sticky='s', rowspan=2)
        ttk.Button(right2, width=w, text='Up')  .grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(right2, width=w, text='Down').grid(row=1, column=0, padx=5)
        #
        three = ttk.Frame(self)  # lower frame for buttons: ok, cancel and apply
        three.grid(row=2, column=0, sticky='e')
        ttk.Button(three, width=w, text='Ok',     command=self.ok)    .pack(side='left', padx=5, pady=5)
        ttk.Button(three, width=w, text='Cancel', command=self.cancel).pack(side='left', padx=5, pady=5)
        ttk.Button(three, width=w, text='Apply',  command=self.apply) .pack(side='left', padx=5, pady=5)
        #
        self.update_idletasks()
        #print(self.geometry())
        self.minsize(self.winfo_width(), self.winfo_height())  # set minimal size

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
