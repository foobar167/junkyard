# Example of the PanedWindow and how to use it
import tkinter as tk
from tkinter import ttk

root = tk.Tk()

w = ttk.PanedWindow(root, orient='horizontal')
w.pack(fill='both', expand='yes')

left = ttk.Frame(w)
left.rowconfigure(0, weight=1)
left.columnconfigure(0, weight=1)
w.add(left, weight=1)
label_left = ttk.Label(left, text='left side', background='red')
label_left.grid(row=0, column=0, sticky='nswe')

right = ttk.Frame(w, width=200, height=200)
right.grid_propagate(0)  # fixed width
right.rowconfigure(0, weight=1)
right.columnconfigure(0, weight=1)
w.add(right, weight=0)
label_right = ttk.Label(right, text='right side', background='blue')
label_right.grid(row=0, column=0, sticky='nswe')

root.mainloop()
