# Example of the PanedWindow and how to use it
import tkinter as tk
from tkinter import ttk

root = tk.Tk()

w1 = ttk.PanedWindow(root, orient='horizontal')
w1.pack(fill='both', expand=1)

left1 = ttk.Label(w1, text='left pane - 1')
w1.add(left1)

right1 = ttk.Label(w1, text='right pane - 1')
w1.add(right1)

one_more = ttk.Label(w1, text='one more pane')
w1.add(one_more)

w2 = ttk.PanedWindow(root, orient='horizontal')
w2.pack(fill='both', expand=1)

left2 = ttk.Label(w2, text='left pane - 2')
w2.add(left2)

right2 = ttk.Label(w2, text='right pane - 2')
w2.add(right2)

root.mainloop()
