# Objects tracking using feature extraction algorithm
import cv2
import numpy as np
import tkinter as tk

from PIL import Image, ImageTk


class Application:
    """ Main GUI Window """
    def __init__(self):
        """ Apply ORB algorithm to track objects """
        self.video_stream = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # capture video stream, '0' is default camera
        self.video_stream.set(cv2.CAP_PROP_FRAME_WIDTH, 960)  # set video resolution to 800×600 or 960×720
        self.video_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # default resolution is 640×480
        self.orb = ORB("./data/2023.06.23_book_cover.jpg")  # initiate ORB object

        self.root_window = tk.Tk()  # initialize root window
        self.root_window.title("ORB tracking")  # set window title
        window_geometry = "1024x768+0+0"  # window geometry 'Width × Height ± X ± Y'
        self.root_window.geometry(window_geometry)  # set window size and position
        # Trigger self.destructor function when the root window is closed
        self.root_window.protocol("WM_DELETE_WINDOW", self.destructor)

        # Create tk.Frame container in GUI and make it expandable
        container = tk.Frame(self.root_window)
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

        self.video_loop()  # start a video loop

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.video_stream.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            if self.orb.image is not None:
                frame = self.orb.tracking(frame)
            frame = self.resize_image(frame)  # resize frame for the GUI window
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert from BGR to RGBA
            image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image
        self.root_window.after(30, self.video_loop)  # call the same function after 30 milliseconds

    def resize_image(self, image):
        """ Resize image proportionally """
        h1, w1 = image.shape[:2]  # color image has shape [h, w, 3]
        w1, h1 = float(w1), float(h1)
        w2, h2 = float(self.panel.winfo_width()), float(self.panel.winfo_height())
        aspect_ratio1 = w1 / h1
        aspect_ratio2 = w2 / h2
        if aspect_ratio1 == aspect_ratio2:
            dim = (int(w2), int(h2))
        elif aspect_ratio1 > aspect_ratio2:
            dim = (int(w2), max(1, int(w2 / aspect_ratio1)))
        else:  # aspect_ratio1 < aspect_ratio2
            dim = (max(1, int(h2 * aspect_ratio1)), int(h2))
        # Interpolation could be: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
        return cv2.resize(image, dim, interpolation=Image.ANTIALIAS)

    def get_snapshot(self):
        """ Get snapshot """
        _, frame = self.video_stream.read()  # read frame from video stream
        self.orb.set_image(frame)  # set snapshot in ORB object
        print("[INFO] get new snapshot")

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.root_window.destroy()
        self.video_stream.release()  # release web camera
        cv2.destroyAllWindows()  # destroy all cv2 windows


class ORB:
    """ ORB feature extractor object """
    def __init__(self, impath=None):
        self.image, self.keypoints, self.descriptor, self.pts = None, None, None, None
        self.orb = cv2.ORB_create()  # initiate ORB detector
        image = cv2.imread(impath)  # return None if image doesn't exist
        self.set_image(image)

        # Set some constant parameters and constant variables
        self.params = {
            "index_params": dict(algorithm=1, trees=5),  # Flann Matcher parameter
            "search_params": dict(checks=50),  # Flann parameter, or pass empty dictionary instead
            "draw_params": dict(outImg=None, matchColor=(127, 255, 127),
                                singlePointColor=(210, 250, 250), flags=0),  # rectangle draw parameters
        }
        self.flann = cv2.FlannBasedMatcher(self.params["index_params"], self.params["search_params"])

    def set_image(self, image):
        """ Set current image with object to track """
        self.image = image
        if image is not None:
            self.keypoints, self.descriptor = self.compute(image)
            h, w = image.shape[:2]  # color image has shape [h, w, 3]
            self.pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)

    def compute(self, image):
        """ Compute keypoints and descriptors """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # color BGR to grayscale
        keypoints, descriptor = self.orb.detectAndCompute(gray, None)
        descriptor = np.float32(descriptor)  # convert from uint8 to float32 for FLANN matcher
        return keypoints, descriptor

    def tracking(self, image):
        """ Draw matches between two images according to ORB algorithm """
        keypoints2, descriptor2 = self.compute(image)
        matches = self.flann.knnMatch(self.descriptor, descriptor2, k=2)

        # Store all the good matches as per David G. Lowe's ratio test
        good_matches = []
        matches_mask = np.zeros((len(matches), 2), dtype=np.int)
        for i, (m, n) in enumerate(matches):
            if m.distance < 0.75 * n.distance:
                matches_mask[i] = [1, 0]
                good_matches.append(m)

        if len(good_matches) > 10:  # draw a rectangle if there are enough matches
            src_pts = np.float32([self.keypoints[m.queryIdx].pt for m in good_matches])
            dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches])
            # Find perspective transformation between two planes
            matrix, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            if matrix is not None:  # not empty
                dst = cv2.perspectiveTransform(self.pts, matrix)  # apply perspective algorithm
                image = cv2.polylines(image, [np.int32(dst)], True, (226, 43, 138), 3)  # color (B,G,R)

        return cv2.drawMatchesKnn(self.image, self.keypoints, image, keypoints2,
                                  matches, matchesMask=matches_mask, **self.params["draw_params"])

    @staticmethod
    def concat(image1, image2):
        """ Concatenate two images """
        h1, w1 = image1.shape[:2]
        h2, w2 = image2.shape[:2]
        if h1 == h2:  # if images are the same height
            return np.concatenate((image1, image2), axis=1)
        # for images with different height create an empty matrix filled with zeros
        image = np.zeros((max(h1, h2), w1+w2, 3), np.uint8)
        # combine two images
        image[:h1, :w1, :3] = image1
        image[:h2, w1:w1+w2, :3] = image2
        return image


# start the app
print("[INFO] starting...")
pba = Application()
pba.root_window.mainloop()
