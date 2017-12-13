# Using lambda keyword to create a dynamic menu.
import tkinter as tk

def f(x):
    print(x)

root = tk.Tk()
menubar = tk.Menu(root)
root.configure(menu=menubar)
menu = tk.Menu(menubar, tearoff=False)
l = ['one', 'two', 'three']
for i in l:
    menu.add_command(label=i, command=lambda x=i: f(x))
menubar.add_cascade(label='File', menu=menu)
root.mainloop()
