# Objects tracking using ORB algorithm for Python 3.x
import cv2
import numpy as np
import tkinter as tk

from PIL import Image, ImageTk


class Application:
    def __init__(self):
        """ Apply ORB algorithm to track objects """
        self.video_stream = cv2.VideoCapture(0)  # capture video stream, '0' is default camera
        #self.orb = cv2.xfeatures2d.ORB_create()
        self.orb = cv2.ORB_create()
        #self.snapshot_image = None  # take snapshot from the camera
        self.snapshot_image = cv2.imread("./data/2023.06.23_book_cover.jpg")  # read any image you like

        self.root_window = tk.Tk()  # initialize root window
        self.root_window.title("ORB tracking")  # set window title
        # self.destructor function is triggered when the root window is closed
        self.root_window.protocol("WM_DELETE_WINDOW", self.destructor)

        self.panel = tk.Label(self.root_window)  # initialize image panel
        self.panel.pack(padx=10, pady=10)  # set padding

        # Button, when pressed, the current frame will be taken
        btn = tk.Button(self.root_window, text="Get snapshot", command=self.get_snapshot)
        btn.pack(fill="both", expand=True, padx=10, pady=10)

        self.video_loop()  # start a video loop


    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.video_stream.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            if self.snapshot_image is not None:
                try:  # sometimes knnMatch and perspectiveTransform methods are throwing an errors
                    frame = self.orb_matches(self.snapshot_image, frame)
                except Exception as e:  # if an error occurs, just concatenate and show 2 images
                    #print(e)  # print error if necessary
                    frame = self.concat(self.snapshot_image, frame)
            # convert colors from BGR to RGBA
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image
        self.root_window.after(30, self.video_loop)  # call the same function after 30 milliseconds


    def orb_matches(self, image1, image2):
        """ Draw matches between two images according to ORB algorithm """
        gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        keypoints1, descriptor1 = self.orb.detectAndCompute(gray1, None)
        keypoints2, descriptor2 = self.orb.detectAndCompute(gray2, None)
        descriptor1 = np.float32(descriptor1)  # convert from uint8 to float32 for FLANN matcher
        descriptor2 = np.float32(descriptor2)
        indexParams = dict(algorithm=0, trees=5)
        searchParams = dict(checks=50)  # or pass empty dictionary
        flann = cv2.FlannBasedMatcher(indexParams, searchParams)
        matches = flann.knnMatch(descriptor1, descriptor2, k=2)

        # Store all the good matches as per David G. Lowe's ratio test
        good = []
        for m,n in matches:
            if m.distance < 0.75 * n.distance:
                good.append(m)

        if len(good) > 20:  # find > 20 matches
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


    def get_snapshot(self):
        """ Get snapshot """
        ret, self.snapshot_image = self.video_stream.read()  # read frame from video stream
        print("[INFO] get new snapshot")


    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.root_window.destroy()
        self.video_stream.release()  # release web camera
        cv2.destroyAllWindows()  # destroy all cv2 windows


# start the app
print("[INFO] starting...")
pba = Application()
pba.root_window.mainloop()
