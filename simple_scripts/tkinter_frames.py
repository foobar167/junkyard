import tkinter as tk

root = tk.Tk()
root.geometry('800x600+0+0')
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=3)
root.columnconfigure(1, weight=1)
f1 = tk.Frame(root, background='blue')
f1.grid(row=0, column=0, sticky='nswe')
f2 = tk.Frame(root, background='green')
f2.grid(row=0, column=1, sticky='nswe')
root.mainloop()
