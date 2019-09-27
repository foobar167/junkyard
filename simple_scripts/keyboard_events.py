# It is possible to use Python + Tkinter to generate keyboard events.
# Tkinter is a part of the Python.
# Note: this is a console application :-)
import tkinter as tk


def keystroke(event):
    print(event.keycode)


def keyboardevent(str):
    # Code that simulated 'key' being pressed on keyboard
    root.after(10, lambda: root.event_generate('<Key-{}>'.format(str)))

root = tk.Tk()
root.withdraw()  # remove the window from the screen (without destroying it)
root.bind('<Key>', keystroke)
keyboardevent('a') # lower case 'a'
keyboardevent('B') # upper case 'B'
keyboardevent('Right') # right arrow key
root.after(20, root.destroy)
root.mainloop()

print('Hello World!')
