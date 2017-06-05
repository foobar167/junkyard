import cv2
import sys
import numpy as np
from PIL import Image, ImageTk

if sys.version_info.major < 3:  # for Python 3.x
    import Tkinter as tk
else:  # for Python 2.x
    import tkinter as tk

class Application:
    def __init__(self):
        """ Apply SIFT algorithm to track objects """
        self.vs = cv2.VideoCapture(0)  # capture video frames, 0 is your default video camera
        self.sift = cv2.xfeatures2d.SIFT_create()
        self.snapshot_image = None  # snapshot from the camera
        #self.snapshot_image = cv2.imread("2017-06-01_13-06-58.jpg")  # read any image you like

        self.root = tk.Tk()  # initialize root window
        self.root.title("SIFT tracking")  # set window title
        # self.destructor function gets fired when the window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.destructor)

        self.panel = tk.Label(self.root)  # initialize image panel
        self.panel.pack(padx=10, pady=10)

        # create a button, that when pressed, will take current frame
        btn = tk.Button(self.root, text="Snapshot!", command=self.take_snapshot)
        btn.pack(fill="both", expand=True, padx=10, pady=10)

        # start a self.video_loop that constantly pools video sensor
        # for the most recently read frame
        self.video_loop()

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            if self.snapshot_image is not None:
                frame = self.sift_matches(self.snapshot_image, frame)
            # convert colors from BGR to RGBA
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image
        self.root.after(30, self.video_loop)  # call the same function after 30 milliseconds

    def sift_matches(self, image1, image2):
        """ Draw matches between two images according to SIFT algorithm """
        try:  # sometimes knnMatch and perspectiveTransform methods are throwing an errors
            gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
            keypoints1, descriptor1 = self.sift.detectAndCompute(gray1, None)
            keypoints2, descriptor2 = self.sift.detectAndCompute(gray2, None)
            indexParams = dict(algorithm=0, trees=5)
            searchParams = dict(checks=50)  # or pass empty dictionary
            flann = cv2.FlannBasedMatcher(indexParams, searchParams)
            matches = flann.knnMatch(descriptor1, descriptor2, k=2)
            # store all the good matches as per David G. Lowe's ratio test
            good = []
            for m,n in matches:
                if m.distance < 0.75 * n.distance:
                    good.append(m)
            if len(good) > 20:
                src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
                dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                matchesMask = mask.ravel().tolist()
                h, w = image1.shape[:2]
                pts = np.float32([[0, 0], [0,h-1], [w-1,h-1], [w-1,0]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, M)
                image2 = cv2.polylines(image2, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
            else:
                matchesMask = None
            drawParams = dict(matchColor=(0, 255, 0),
                              singlePointColor=None,
                              matchesMask=matchesMask,
                              flags=2)
            return cv2.drawMatches(image1, keypoints1, image2, keypoints2, good, None, **drawParams)
        except:  # if error occured, just concatenate and show 2 images
            return self.concat(image1, image2)

    def concat(self, image1, image2):
        """ Concatenate two images """
        h1, w1 = image1.shape[:2]
        h2, w2 = image2.shape[:2]
        if h1 == h2: # if images are the same height
            return np.concatenate((image1, image2), axis=1)
        # for images with different height create an empty matrix filled with zeros
        image = np.zeros((max(h1,h2), w1+w2, 3), np.uint8)
        # combine two images
        image[:h1, :w1, :3] = image1
        image[:h2, w1:w1+w2, :3] = image2
        return image

    def take_snapshot(self):
        """ Take snapshot """
        ret, self.snapshot_image = self.vs.read()  # read frame from video stream
        print("[INFO] new snapshot")

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.root.destroy()
        self.vs.release()  # release web camera
        cv2.destroyAllWindows()  # destroy all cv2 windows

# start the app
print("[INFO] starting...")
pba = Application()
pba.root.mainloop()

