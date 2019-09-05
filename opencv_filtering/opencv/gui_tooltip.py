# -*- coding: utf-8 -*-
import tkinter as tk

from time import time


class ToolTip(tk.Toplevel):
    """ ToolTip widget for Tkinter """
    def __init__(self, widget, msg=None, func=None, delay=0.5, follow=False):
        """ Initialize the ToolTip.
            Arguments:
                widget - The widget this ToolTip is assigned to
                msg    - A static string message assigned to the ToolTip
                func   - A function that retrieves a string to use as the ToolTip text
                delay  - The delay in seconds before the ToolTip appears(may be float)
                follow - If True, the ToolTip follows motion, otherwise hides """
        self.widget = widget
        # The parent of the ToolTip is the parent of the ToolTips widget
        tk.Toplevel.__init__(self, self.widget.master, bg='black', padx=1, pady=1)
        self.withdraw()  # hide initially - tk.Toplevel.withdraw()
        self.overrideredirect(True)  # should not have frame or title bar
        self.msgVar = tk.StringVar()  # contain the text displayed by the ToolTip
        self.msg = msg
        if self.msg == None:
            self.msgVar.set('No message provided')
        else:
            self.msgVar.set(self.msg)
        self.func = func  #
        self.delay = delay  # delay in showing tooltip
        self.follow = follow  # follow the cursor
        self.visible = 0
        self.lastMotion = 0
        # The text of the ToolTip is displayed in a Message widget
        tk.Message(self, textvariable=self.msgVar, bg='#FFFFDD', aspect=1000).grid()
        # Add bindings to the widget. This will NOT override bindings that the widget already has.
        self.widget.bind('<Enter>', self.spawn, True)
        self.widget.bind('<Leave>', self.hide, True)
        self.widget.bind('<Motion>', self.move, True)
        self.widget.bind('<Button-1>', self.hide, True)

    def spawn(self, event=None):
        """ Make the ToolTip eligible for display """
        self.visible = 1
        self.after(int(self.delay * 1000), self.show)  # show after <delay> ms

    def show(self):
        """ Display the ToolTip if the time delay has been long enough """
        if self.visible == 1 and float(time() - self.lastMotion) > self.delay:
            self.visible = 2
        if self.visible == 2:
            self.deiconify()  # tk.Toplevel.deiconify()

    def move(self, event):
        """ Process motion within the widget """
        self.lastMotion = time()
        # If the follow flag is not set, motion within the widget will make the ToolTip disappear.
        if not self.follow:
            self.withdraw()  # hide initially - tk.Toplevel.withdraw()
            self.visible = 1
        # Offset the ToolTip 10x10 pixes southeast of the pointer
        self.geometry('+{x}+{y}'.format(x = event.x_root + 10, y = event.y_root + 10))
        msg = None
        try:  # the message is unchanged if function is None or fails
            msg = self.func()  # execute some function if necessary and get its output
            self.msgVar.set(msg)  # set function output message to the tooltip
        except:
            pass
        if self.msg or msg:  # show only non-empty messages
            self.after(int(self.delay * 1000), self.show)

    def hide(self, event=None):
        """ Hide the ToolTip """
        self.visible = 0
        self.withdraw()
