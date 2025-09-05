# Status of control, shift and control+shift keys in Python
import tkinter as tk

ctrl = False
shift = False
ctrl_shift = False

def key(event):
    global ctrl, shift, ctrl_shift
    #print(event.keycode, event.keysym, event.state)
    if ctrl_shift:
        print('<Ctrl>+<Shift>+{}'.format(event.keysym))
    elif ctrl:
        print('<Ctrl>+{}'.format(event.keysym))
    elif shift:
        print('<Shift>+{}'.format(event.keysym))
    ctrl = False
    shift = False
    ctrl_shift = False

def control_key(state, event=None):
    ''' Controll button is pressed or released '''
    global ctrl
    ctrl = state

def shift_key(state, event=None):
    ''' Controll button is pressed or released '''
    global shift
    shift = state
    control_shift(state)

def control_shift(state):
    ''' <Ctrl>+<Shift> buttons are pressed or released '''
    global ctrl, ctrl_shift
    if ctrl == True and state == True:
        ctrl_shift = True
    else:
        ctrl_shift = False

root = tk.Tk()
root.geometry('256x256+0+0')

root.event_add('<<ControlOn>>',  '<KeyPress-Control_L>',   '<KeyPress-Control_R>')
root.event_add('<<ControlOff>>', '<KeyRelease-Control_L>', '<KeyRelease-Control_R>')
root.event_add('<<ShiftOn>>',    '<KeyPress-Shift_L>',     '<KeyPress-Shift_R>')
root.event_add('<<ShiftOff>>',   '<KeyRelease-Shift_L>',   '<KeyRelease-Shift_R>')

root.bind('<<ControlOn>>', lambda e: control_key(True))
root.bind('<<ControlOff>>', lambda e: control_key(False))
root.bind('<<ShiftOn>>', lambda e: shift_key(True))
root.bind('<<ShiftOff>>', lambda e: shift_key(False))
root.bind('<Key>', key)

root.mainloop()
