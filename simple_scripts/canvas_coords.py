# Display canvas coordinates when hovering cursor over canvas
# When hover over the canvas, display (x,y) coordinates.
import tkinter

root = tkinter.Tk()
canvas = tkinter.Canvas(root)
canvas.pack()

def get_coordinates(event):
    canvas.itemconfigure(tag, text=f'({event.x}, {event.y})')

canvas.bind('<Motion>', get_coordinates)
canvas.bind('<Enter>', get_coordinates)  # handle <Alt>+<Tab> switches between windows
tag = canvas.create_text(10, 10, text='', anchor='nw')

root.mainloop()
