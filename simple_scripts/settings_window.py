# -*- coding: utf-8 -*-
# Modal dialog settings/configure window for the bigger project
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

class AutoScrollbar(ttk.Scrollbar):
    """ A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager """
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')

class MainGUI(ttk.Frame):
    """ Main GUI window """
    def __init__(self, master):
        """ Init main window """
        ttk.Frame.__init__(self, master=master)
        self.master.title('Main GUI')
        self.master.geometry('300x200')
        self.size = (320, 240)  # size of the frame in pixels
        self.list = ['one', 'two', 'three', 'four', 'five', 'very long interesting class name', 'six',
                     'seven', 'eight', 'nine', 'ten', 'eleven', 'ok?']
        #self.state = 'disabled'
        self.state = 'normal'
        b = ttk.Button(self.master, text='Settings', command=self.open_settings)
        b.pack()
        b.focus_set()

    def open_settings(self):
        """ Open settings modal window """
        s = Settings(self)  # create settings object
        self.master.wait_window(s)  # display the settings window and wait for it to close

class Settings(simpledialog.Dialog):
    """ Settings / configure window for bigger project """
    def __init__(self, parent):
        """ Init settings window """
        tk.Toplevel.__init__(self, master=parent)
        self.create_settings_window()
        self.create_widgets()

    def create_settings_window(self):
        """ Create setting window """
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
        """ Widgets for settings window are created here """
        w = 12  # width of the buttons and entry
        vcmd_size = (self.register(self.validate_size),
                     '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')  # size validator
        vcmd_classname = (self.register(self.validate_classname),
                          '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')  # classname validator
        #
        self.rowconfigure(0, weight=1)  # make top frame extendable
        self.columnconfigure(0, weight=1)
        top = ttk.Frame(self)  # upper frame with settings
        top.grid(row=0, column=0, sticky='nswe')
        top.rowconfigure(2, weight=1)  # make ListBox extendable
        top.columnconfigure(1, weight=1)
        #
        # Frame size widget
        self.entry1 = tk.IntVar()  # bind the entry widget to the IntVar
        self.entry2 = tk.IntVar()  # bind the entry widget to the IntVar
        ttk.Label(top, text='Frame size: ').grid(row=0, column=0, sticky='w', pady=5)
        sizebox = ttk.Frame(top)  # frame for roi width and height
        sizebox.grid(row=0, column=1, sticky='w', columnspan=3, pady=5)
        self.e1 = ttk.Entry(sizebox, state=self.master.state, textvariable=self.entry1,
                            validate='key', validatecommand=vcmd_size)  # width
        self.e1.pack(side='left')
        ttk.Label(sizebox, text='x').pack(side='left')
        self.e2 = ttk.Entry(sizebox, state=self.master.state, textvariable=self.entry2,
                            validate='key', validatecommand=vcmd_size)  # height
        self.e2.pack(side='left')
        #
        # New classname widget
        ttk.Label(top, text='New class name: ').grid(row=1, column=0, sticky='w')
        self.entry3 = tk.StringVar()  # bind the entry widget to the StringVar
        e3 = ttk.Entry(top, width=w, textvariable=self.entry3,
                       validate='key', validatecommand=vcmd_classname)
        e3.grid(row=1, column=1, columnspan=2, sticky='we')
        e3.focus_set()  # set focus on this entry widget
        e3.bind('<Return>', self.add)  # add classname when press Enter key
        #
        # ListBox widget
        vbar = AutoScrollbar(top, orient='vertical')  # vertical and horizontal scrollbars
        hbar = AutoScrollbar(top, orient='horizontal')
        vbar.grid(row=2, column=2, sticky='ns')
        hbar.grid(row=3, column=0, sticky='we', columnspan=2)
        self.listbox = tk.Listbox(top, xscrollcommand=hbar.set, yscrollcommand=vbar.set,
                                  selectmode='browse')  # browse == use only 1 selection at a time
        self.listbox.grid(row=2, column=0, sticky='nswe', columnspan=2, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)  # selection event
        self.listbox.bind('<Delete>', self.remove)  # deletion event
        self.listbox.bind('<FocusIn>', self.on_focus)  # focus-in event
        hbar.configure(command=self.listbox.xview)  # bind scrollbars with ListBox
        vbar.configure(command=self.listbox.yview)
        #
        # Insert data into Settings window
        self.e1.configure(width=len(str(self.master.size[0])))  # set width of the entry widgets
        self.e2.configure(width=len(str(self.master.size[1])))
        self.entry1.set(self.master.size[0])  # set frame size into the entry widgets
        self.entry2.set(self.master.size[1])
        self.listbox.insert('end', *self.master.list)  # fill ListBox with data
        #
        box1 = ttk.Frame(top)  # top right frame container with buttons
        box1.grid(row=1, column=3, sticky='n', rowspan=2)
        self.button_add = ttk.Button(box1, width=w, state='disabled',
                                     text='Add', command=self.add)
        self.button_add.grid(row=0, column=0, padx=5)
        self.button_remove = ttk.Button(box1, width=w, state='disabled',
                                        text='Remove', command=self.remove)
        self.button_remove.grid(row=1, column=0, padx=5, pady=5)
        #
        box2 = ttk.Frame(top)  # bottom right frame container with buttons
        box2.grid(row=2, column=3, sticky='s', rowspan=2)
        self.button_up = ttk.Button(box2, width=w, state='disabled',
                                    text='Up', command=self.up)
        self.button_up.grid(row=0, column=0, padx=5)
        self.button_down = ttk.Button(box2, width=w, state='disabled',
                                      text='Down', command=self.down)
        self.button_down.grid(row=1, column=0, padx=5, pady=5)
        #
        box3 = ttk.Frame(self)  # bottom frame with buttons: ok, cancel and apply
        box3.grid(row=1, column=0, sticky='e')
        ttk.Button(box3, width=w, text='Ok',
                   command=self.ok).pack(side='left', padx=5, pady=5)
        ttk.Button(box3, width=w, text='Cancel',
                   command=self.cancel).pack(side='left', pady=5)
        self.button_apply = ttk.Button(box3, width=w, state='disabled',
                                       text='Apply', command=self.apply)
        self.button_apply.pack(side='left', padx=5, pady=5)
        #
        self.update_idletasks()  # wait untill window is created
        self.minsize(self.winfo_width(), self.winfo_height())  # set minimal size

    def validate_change(self):
        """ Validate if changes are made and enable/disable Apply button """
        if  self.entry1.get() == self.master.size[0] and \
            self.entry2.get() == self.master.size[1] and \
            self.listbox.get(0, 'end') == tuple(self.master.list):
            self.button_apply.configure(state='disabled')
            return False
        else:
            self.button_apply.configure(state='normal')
            return True

    def validate_size(self, d, i, P, s, S, v, V, W):
        """ Validate only digits for the size in pixels """
        # Validation parameters
        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %i = index of char string to be inserted/deleted, or -1
        # %P = value of the entry if the edit is allowed
        # %s = value of entry prior to editing
        # %S = the text string being inserted or deleted, if any
        # %v = the type of validation that is currently set
        # %V = the type of validation that triggered the callback
        #      (key, focusin, focusout, forced)
        # %W = the tk name of the widget
        if P.isdigit() or P == '':
            # Change width of the entry widget according to the new length
            self.master.nametowidget(W).configure(width=len(str(P)))  # fit the entry width
            self.after_idle(self.validate_change)  # enable/disable Apply button after some time
            return True
        self.bell()
        return False

    def validate_classname(self, d, i, P, s, S, v, V, W):
        """ Validate string for class name """
        for j in S:  # Could enter alphanumeric or some other symbols
            if j.isalpha() or j.isdigit() or j in '., -_@':
                classname = P.strip()  # strip opening and trailing spaces
                if classname and classname not in self.listbox.get(0, 'end'):
                    self.button_add.configure(state='normal')  # enable Add button
                else:
                    self.button_add.configure(state='disabled')  # disable Add button
                return True
        self.bell()
        return False

    def on_select(self, event=None):
        """ Enable/disable buttons on selection of the ListBox item """
        if self.listbox.curselection():  # if selection
            self.button_remove.configure(state='normal')
            self.button_up.configure(state='normal')
            self.button_down.configure(state='normal')
        else:
            self.button_remove.configure(state='disabled')
            self.button_up.configure(state='disabled')
            self.button_down.configure(state='disabled')

    def on_focus(self, event=None):
        """ LisbBox obtains focus """
        if self.listbox.curselection(): return  # selection already exists
        if tk.ACTIVE:  # active item exists
            self.listbox.selection_set('active')  # select active item
            self.listbox.see('active')  # make active item visible
            self.listbox.event_generate('<<ListboxSelect>>')  # generate selection event

    def add(self, event=None):
        """ Add classname to the list """
        classname = self.entry3.get()  # get classname from the entry
        classname = classname.strip()  # strip opening and trailing spaces
        if classname and classname not in self.listbox.get(0, 'end'):
            self.listbox.insert(0, classname)  # add new class name to the list
            self.entry3.set('')  # empty entry widget
            self.button_add.configure(state='disabled')  # disable Add button
            self.validate_change()  # enable/disable Apply button

    def remove(self, event=None):
        """ Remove classname from the list """
        if self.listbox.curselection():  # if selected
            index = self.listbox.curselection()[0]  # get index of selected item
            self.listbox.delete(index)  # delete selected item
            self.button_remove.configure(state='disabled')  # disable Remove button
            self.button_up.configure(state='disabled')
            self.button_down.configure(state='disabled')
            self.validate_change()  # enable/disable Apply button

    def up(self):
        """ Move classname upwards in the LisbBox """
        if self.listbox.curselection():  # if selected
            index = self.listbox.curselection()[0]  # get index of selected item
            self.listbox.see(index)  # make selected item visible
            if index == 0: return  # first item cannot go upwards
            classname = self.listbox.get(index)  # get selected class name
            self.listbox.insert(index-1, classname)  # move item upwards
            self.listbox.delete(index+1)  # delete selected item
            self.listbox.activate(index-1)  # activate moved item
            self.listbox.selection_set(index-1)  # select moved item
            self.listbox.see(index-1)  # make moved item visible
            self.validate_change()  # enable/disable Apply button

    def down(self):
        """ Move classname downwards in the LisbBox """
        if self.listbox.curselection():  # if selected
            index = self.listbox.curselection()[0]  # get index of selected item
            self.listbox.see(index)  # make selected item visible
            if index == self.listbox.size() - 1: return  # last item cannot go downwards
            classname = self.listbox.get(index)  # get selected class name
            self.listbox.insert(index+2, classname)  # move item downwards
            self.listbox.delete(index)  # delete selected item
            self.listbox.activate(index+1)  # activate moved item
            self.listbox.selection_set(index+1)  # select moved item
            self.listbox.see(index+1)  # make moved item visible
            self.validate_change()  # enable/disable Apply button

    def apply(self):
        """ Apply settings changes """
        if self.validate_change():
            self.master.size = (self.entry1.get(), self.entry2.get())
            self.master.list = list(self.listbox.get(0, 'end'))
            self.button_apply.configure(state='disabled')

    def ok(self, event=None):
        """ Apply changes and close settings window """
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        """ Close settings window """
        self.master.focus_set()  # put focus back to the parent window
        self.destroy()  # destroy settings window

root = tk.Tk()
feedback = MainGUI(root)
root.mainloop()
