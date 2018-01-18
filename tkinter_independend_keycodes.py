# 1. Generate keystrokes using Python + Tkinter.
# 2. Save needed keycodes in the dictionary.
# 3. Use dictionary with keycodes to handle keystrokes independently from
#    operating system, language or (maybe?) keyboard model.
# This is not an elegant solution, so I think it is better to "hardcode"
# keycodes depending on the operating system.
import tkinter as tk

def keystroke(event):
    dict[event.keycode] = event.keysym  # save keycodes into the dictionary

def keyboardevent(str):
    # Code that simulated 'key' being pressed on keyboard
    temp.after(10, lambda: temp.event_generate('<Key-{}>'.format(str)))

temp = tk.Tk()
temp.withdraw()  # remove the window from the screen (without destroying it)
temp.bind('<Key>', keystroke)
dict = {}  # dictionary of the needed keycodes
keyboardevent('w')  # generate needed keyboard events
keyboardevent('s')
keyboardevent('a')
keyboardevent('d')
temp.after(20, temp.destroy)  # this is not needed anymore
temp.mainloop()

# Start your code here
def keys_handler(event):
    if event.keycode in dict:
        print(dict[event.keycode])

root = tk.Tk()
root.focus_force()
root.bind('<Key>', keys_handler)
root.mainloop()
