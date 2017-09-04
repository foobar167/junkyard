import sys

if sys.version_info.major < 3:  # for Python 2.x
    import Tkinter as tk
else:  # for Python 3.x
    import tkinter as tk

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master.title("Conversion application")
        self.master.geometry("300x100")
        self.x = tk.IntVar()
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        self.e = tk.Entry(self, textvariable=self.x)
        self.e.bind('<Return>', self.convert)
        self.e.focus()
        self.e.grid()
        self.b = tk.Button(self, text="Convert", command=self.convert)
        self.b.grid()
        self.l = tk.Label(self)
        self.l.grid()

    def convert(self, event=None):
        try:
            print(self.x.get())
            conversion = self.x.get()
            conversion = conversion * 1.8 + 32
            self.l.config(text=conversion)
        except tk.TclError:
            self.l.config(text="Not an integer")

app = Application()
app.mainloop()
