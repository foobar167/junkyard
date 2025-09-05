import tkinter as tk
from tkinter import ttk
from time import time, localtime, strftime


class ToolTip(tk.Toplevel):
    ''' ToolTip widget for Tkinter '''
    def __init__(self, wdgt, msg=None, func=None, delay=1.0, follow=True):
        ''' Initialize the ToolTip.
            Arguments:
                wdgt:   The widget this ToolTip is assigned to
                msg:    A static string message assigned to the ToolTip
                func:   A function that retrieves a string to use as the ToolTip text
                delay:  The delay in seconds before the ToolTip appears(may be float)
                follow: If True, the ToolTip follows motion, otherwise hides '''
        self.wdgt = wdgt
        # The parent of the ToolTip is the parent of the ToolTips widget
        tk.Toplevel.__init__(self, self.wdgt.master, bg='black', padx=1, pady=1)
        self.withdraw()  # hide initially
        self.overrideredirect(True)  # should not have frame or title bar
        self.msgVar = tk.StringVar()  # contain the text displayed by the ToolTip
        if msg == None:
            self.msgVar.set('No message provided')
        else:
            self.msgVar.set(msg)
        self.func = func
        self.delay = delay
        self.follow = follow
        self.visible = 0
        self.lastMotion = 0
        # The text of the ToolTip is displayed in a Message widget
        tk.Message(self, textvariable=self.msgVar, bg='#FFFFDD', aspect=1000).grid()
        # Add bindings to the widget. This will NOT override bindings that the widget already has.
        self.wdgt.bind('<Enter>', self.spawn, '+')
        self.wdgt.bind('<Leave>', self.hide, '+')
        self.wdgt.bind('<Motion>', self.move, '+')

    def spawn(self, event=None):
        ''' Make the ToolTip eligible for display '''
        self.visible = 1
        self.after(int(self.delay * 1000), self.show)

    def show(self):
        ''' Display the ToolTip if the time delay has been long enough '''
        if self.visible == 1 and float(time() - self.lastMotion) > self.delay:
            self.visible = 2
        if self.visible == 2:
            self.deiconify()

    def move(self, event):
        ''' Process motion within the widget '''
        self.lastMotion = time()
        # If the follow flag is not set, motion within the widget will make the ToolTip dissapear.
        if self.follow == False:
            self.withdraw()
            self.visible = 1
        # Offset the ToolTip 10x10 pixes southeast of the pointer
        self.geometry('+{x}+{y}'.format(x = event.x_root + 10, y = event.y_root + 10))
        try:  # the message is unchanged if function is None or fails
            self.msgVar.set(self.func())
        except:
            pass
        self.after(int(self.delay * 1000), self.show)

    def hide(self, event=None):
        ''' Hide the ToolTip '''
        self.visible = 0
        self.withdraw()


def range2d(n, m):
    ''' Return a list of values in a 2d range.
        Arguments:
            n: The number of rows in the 2d range
            m: The number of columns in the 2d range '''
    return [(i, j) for i in range(n) for j in range(m)]


def print_time():
    ''' Print the current time in the following format: time=HH:MM:SS '''
    t = time()
    timeString = 'time='
    timeString += strftime('%H:%M:%S', localtime(t))
    return timeString


def main():
    root = tk.Tk()
    btnList = []
    for (i, j) in range2d(6, 4):
        text = 'delay={}\n'.format(i)
        delay = i
        if j >= 2:
            follow=True
            text += '+follow\n'
        else:
            follow = False
            text += '-follow\n'
        if j % 2 == 0:
            msg = None
            func = print_time
            text += 'Message Function'
        else:
            msg = 'Button at {}'.format(str((i, j)))
            func = None
            text += 'Static Message'
        btnList.append(ttk.Button(root, text=text))
        ToolTip(btnList[-1], msg=msg, func=func, follow=follow, delay=delay)
        btnList[-1].grid(row=i, column=j, sticky='nswe')
    root.mainloop()


if __name__ == '__main__':
    main()
