# -*- coding: utf-8 -*-
# Modal dialog window with Progressbar for the bigger project
import time
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
        self.lst = [
            'Bushes01.png',  'Bushes02.png', 'Bushes03.png', 'Bushes04.png', 'Bushes05.png',
            'Forest01.png',  'Forest02.png', 'Forest03.png', 'Forest04.png', 'Road01.png',
            'Road02.png',    'Road03.png',   'Lake01.png',   'Lake02.png',   'Field01.png']
        b = ttk.Button(self.master, text='Start', command=self.start_progress)
        b.pack()
        b.focus_set()

    def start_progress(self):
        ''' Open modal window '''
        s = ProgressWindow(self, 'MyTest', self.lst)  # create progress window
        self.master.wait_window(s)  # display the window and wait for it to close

class ProgressWindow(simpledialog.Dialog):
    def __init__(self, parent, name, lst):
        ''' Init progress window '''
        tk.Toplevel.__init__(self, master=parent)
        self.name = name
        self.lst = lst
        self.length = 400
        #
        self.create_window()
        self.create_widgets()

    def create_window(self):
        ''' Create progress window '''
        self.focus_set()  # set focus on the ProgressWindow
        self.grab_set()  # make a modal window, so all events go to the ProgressWindow
        self.transient(self.master)  # show only one window in the task bar
        #
        self.title(u'Calculate something for {}'.format(self.name))
        self.resizable(False, False)  # window is not resizable
        # self.close gets fired when the window is destroyed
        self.protocol(u'WM_DELETE_WINDOW', self.close)
        # Set proper position over the parent window
        dx = (self.master.master.winfo_width() >> 1) - (self.length >> 1)
        dy = (self.master.master.winfo_height() >> 1) - 50
        self.geometry(u'+{x}+{y}'.format(x = self.master.winfo_rootx() + dx,
                                         y = self.master.winfo_rooty() + dy))
        self.bind(u'<Escape>', self.close)  # cancel progress when <Escape> key is pressed

    def create_widgets(self):
        ''' Widgets for progress window are created here '''
        self.var1 = tk.StringVar()
        self.var2 = tk.StringVar()
        self.num = tk.IntVar()
        self.maximum = len(self.lst)
        self.tmp_str = ' / ' + str(self.maximum)
        #
        # pady=(0,5) means margin 5 pixels to bottom and 0 to top
        ttk.Label(self, textvariable=self.var1).pack(anchor='w', padx=2)
        self.progress = ttk.Progressbar(self, maximum=self.maximum, orient='horizontal',
                                        length=self.length, variable=self.num, mode='determinate')
        self.progress.pack(padx=2, pady=2)
        ttk.Label(self, textvariable=self.var2).pack(side='left', padx=2)
        ttk.Button(self, text='Cancel', command=self.close).pack(anchor='e', padx=1, pady=(0, 1))
        #
        self.next()

    def next(self):
        ''' Take next file from the list and do something with it '''
        n = self.num.get()
        self.do_something_with_file(n+1, self.lst[n])  # some useful operation
        self.var1.set('File name: ' + self.lst[n])
        n += 1
        self.var2.set(str(n) + self.tmp_str)
        self.num.set(n)
        if n < self.maximum:
            self.after(500, self.next)  # call itself after some time
        else:
            self.close()  # close window

    def do_something_with_file(self, number, name):
        ''' Some useful operation is here '''
        print(number, name)

    def close(self, event=None):
        ''' Close progress window '''
        if self.progress['value'] == self.maximum:
            print('Ok: process finished successfully')
        else:
            print('Cancel: process is cancelled')
        self.master.focus_set()  # put focus back to the parent window
        self.destroy()  # destroy progress window

root = tk.Tk()
feedback = MainGUI(root)
root.mainloop()
