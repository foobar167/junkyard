# Using lambda keyword and refresh function to create a dynamic menu.
import tkinter as tk

def show(x):
    """ Show your choice """
    global label
    new_label = 'Choice is: ' + x
    menubar.entryconfigure(label, label=new_label)  # change menu text
    label = new_label  # update menu label to find it next time
    choice.set(x)

def refresh():
    """ Refresh menu contents """
    global label, l
    if l[0] == 'one':
        l = ['four', 'five', 'six', 'seven']
    else:
        l = ['one', 'two', 'three']
    choice.set('')
    menu.delete(0, 'end')  # delete previous contents of the menu
    menubar.entryconfigure(label, label=const_str)  # change menu text
    label = const_str  # update menu label to find it next time
    for i in l:
        menu.add_command(label=i, command=lambda x=i: show(x))

root = tk.Tk()
# Set some variables
choice = tk.StringVar()
const_str = 'Choice'
label = const_str
l = ['dummy']
# Create some widgets
menubar = tk.Menu(root)
root.configure(menu=menubar)
menu = tk.Menu(menubar, tearoff=False)
menubar.add_cascade(label=label, menu=menu)
b = tk.Button(root, text='Refresh menu', command=refresh)
b.pack()
b.invoke()
tk.Label(root, textvariable=choice).pack()
root.mainloop()
