import cv2
import tkinter as tk

from PIL import Image, ImageTk


class Display:
    """ Display canvas with image and button """
    def __init__(self, gui, extractor):
        """ Set web camera, searchable image, snapshot button, etc. to display on GUI """
        self.video_stream = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # capture video stream, '0' is default camera
        self.video_stream.set(cv2.CAP_PROP_FRAME_WIDTH, 960)  # set video resolution to 800×600 or 960×720
        self.video_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # default resolution is 640×480
        self.extractor = extractor  # feature extractor object
        # Create tk.Frame container in GUI and make it expandable
        container = tk.Frame(gui)
        container.pack(fill=tk.BOTH, expand=1)
        # Configure the rows and columns to have a non-zero weight so that they will take up the extra space
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        self.panel = tk.Label(container, text="Web camera image", anchor="center")  # initialize image panel
        self.panel.grid(row=0, column=0, sticky="nswe")  # make tk.Label expandable
        # Button, when pressed, the current frame will be taken
        buttons = tk.Label(container)  # initialize buttons panel
        buttons.grid(row=1, column=0, sticky="we")
        btn = tk.Button(buttons, text="Get snapshot", command=self.get_snapshot)
        btn.pack(fill="both", expand=True, padx=10, pady=5)
        #
        self.video_loop()  # start a video loop

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.video_stream.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            if self.extractor.image is not None:
                frame = self.extractor.tracking(frame)
            frame = self.resize_image(frame)  # resize frame for the GUI window
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert from BGR to RGBA
            image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image
        # Try to not set 1 ms or less than 10 ms, because the app will lag.
        self.panel.after(10, self.video_loop)  # call the same function after 10 milliseconds

    def resize_image(self, image):
        """ Resize image proportionally """
        h1, w1 = image.shape[:2]  # color image has shape [h, w, 3]
        w1, h1 = float(w1), float(h1)
        w2, h2 = float(self.panel.winfo_width()), float(self.panel.winfo_height())
        aspect_ratio1 = w1 / h1
        aspect_ratio2 = w2 / h2
        if aspect_ratio1 == aspect_ratio2:
            shape = (int(w2), int(h2))
        elif aspect_ratio1 > aspect_ratio2:
            shape = (int(w2), max(1, int(w2 / aspect_ratio1)))
        else:  # aspect_ratio1 < aspect_ratio2
            shape = (max(1, int(h2 * aspect_ratio1)), int(h2))
        # Interpolation could be: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
        return cv2.resize(image, shape, interpolation=Image.ANTIALIAS)

    def get_snapshot(self):
        """ Get snapshot """
        _, frame = self.video_stream.read()  # read frame from video stream
        self.extractor.set_image(frame)  # set snapshot in feature extractor object
        print("[INFO] get new snapshot")

    def destroy(self):
        """ Release all resources """
        self.video_stream.release()  # release web camera
        cv2.destroyAllWindows()  # destroy all cv2 windows
