# Using lambda keyword and refresh function to create a dynamic menu.
import tkinter as tk

def show(x):
    """ Show menu items """
    var.set(x)

def refresh(l):
    """ Refresh menu contents """
    var.set('')
    menu.delete(0, 'end')
    for i in l:
        menu.add_command(label=i, command=lambda x=i: show(x))

root = tk.Tk()
menubar = tk.Menu(root)
root.configure(menu=menubar)
menu = tk.Menu(menubar, tearoff=False)
menubar.add_cascade(label='Choice', menu=menu)

var = tk.StringVar()
l = ['one', 'two', 'three']
refresh(l)
l = ['four', 'five', 'six', 'seven']
tk.Button(root, text='Refresh', command=lambda: refresh(l)).pack()
tk.Label(root, textvariable=var).pack()
root.mainloop()
