import os
import cv2
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk


class Video(ttk.Frame):
    def __init__(self, mainframe):
        ''' Initialize application which uses OpenCV + Tkinter to display and save video stream '''
        ttk.Frame.__init__(self, master=mainframe)
        self.master.title('Save video streem into file')
        self.vs = cv2.VideoCapture(0)  # capture video frames, 0 is your default video camera
        # self.destructor function gets fired when the window is closed
        self.master.protocol("WM_DELETE_WINDOW", self.destructor)
        # Initialize image panel
        self.panel = tk.Label(self.master)
        self.panel.pack()
        # Prepare directory and file
        path = 'Temp'
        if not os.path.isdir(path):  # create path if not exist
            os.makedirs(path)
        dt = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')[:-3]
        filename = os.path.join(path, 'video_{dt}.avi'.format(dt=dt))
        # Initialize video output
        codec = cv2.VideoWriter_fourcc(*'DIVX')
        self.video_out = cv2.VideoWriter(filename, codec, 20.0, (640, 480))
        self.video_loop()

    def video_loop(self):
        ''' Get frame from video stream, show it and save it into a video file '''
        ok, frame = self.vs.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            self.video_out.write(frame)  # write frame to video output
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image
        self.master.after(30, self.video_loop)  # call the same function after 30 milliseconds

    def destructor(self):
        ''' Destroy the main window and and release all resources '''
        self.video_out.release()  # release video output file
        self.master.destroy()  # destroy main window
        self.vs.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application


root = tk.Tk()
app = Video(root)
root.mainloop()
