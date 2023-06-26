# Objects tracking using ORB algorithm for Python 3.x
import cv2
import numpy as np
import tkinter as tk

from PIL import Image, ImageTk


class Application:
    def __init__(self):
        """ Apply ORB algorithm to track objects """
        self.video_stream = cv2.VideoCapture(0)  # capture video stream, '0' is default camera
        self.orb = cv2.ORB_create()  # initiate ORB detector
        # self.snapshot_image = None  # take snapshot from the camera
        self.snapshot_image = cv2.imread("./data/2023.06.23_book_cover.jpg")  # read any image you like

        self.root_window = tk.Tk()  # initialize root window
        self.root_window.title("ORB tracking")  # set window title
        # Trigger self.destructor function when the root window is closed
        self.root_window.protocol("WM_DELETE_WINDOW", self.destructor)

        self.panel = tk.Label(self.root_window)  # initialize image panel
        self.panel.pack(padx=10, pady=10)  # set padding for image panel

        # Button, when pressed, the current frame will be taken
        btn = tk.Button(self.root_window, text="Get snapshot", command=self.get_snapshot)
        btn.pack(fill="both", expand=True, padx=10, pady=10)

        self.video_loop()  # start a video loop

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.video_stream.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            if self.snapshot_image is not None:
                frame = self.orb_matches(self.snapshot_image, frame)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert from BGR to RGBA
        image = Image.fromarray(cv2image)  # convert image for PIL
        imgtk = ImageTk.PhotoImage(image=image)  # convert image for tkinter
        self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
        self.panel.config(image=imgtk)  # show the image
        self.root_window.after(30, self.video_loop)  # call the same function after 30 milliseconds

    def orb_matches(self, image1, image2):
        """ Draw matches between two images according to ORB algorithm """
        gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        keypoint1, descriptor1 = self.orb.detectAndCompute(gray1, None)
        keypoint2, descriptor2 = self.orb.detectAndCompute(gray2, None)
        descriptor1 = np.float32(descriptor1)  # convert from uint8 to float32 for FLANN matcher
        descriptor2 = np.float32(descriptor2)
        index_params = dict(algorithm=1, trees=5)  # FLANN_INDEX_KDTREE = 1
        search_params = dict(checks=50)  # or pass empty dictionary instead
        flann = cv2.FlannBasedMatcher(index_params, search_params)  # Flann Matcher
        matches = flann.knnMatch(descriptor1, descriptor2, k=2)

        # Store all the good matches as per David G. Lowe's ratio test
        good_matches = []
        matches_mask = [[0, 0] for _ in range(len(matches))]
        for i, (m, n) in enumerate(matches):
            if m.distance < 0.75 * n.distance:
                matches_mask[i] = [1, 0]
                good_matches.append(m)

        if len(good_matches) > 10:  # draw a rectangle if there are enough matches
            src_pts = np.float32([keypoint1[m.queryIdx].pt for m in good_matches])
            dst_pts = np.float32([keypoint2[m.trainIdx].pt for m in good_matches])

            # Find perspective transformation between two planes
            matrix, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            if matrix is not None:  # if not empty
                h, w = image1.shape[:2]  # color image has shape [h, w, 3]
                pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, matrix)  # apply perspective algorithm
                image2 = cv2.polylines(image2, [np.int32(dst)], True, (226, 43, 138), 3)  # BGR = (255,0,0)

        draw_params = dict(outImg=None, matchColor=(127, 255, 127), singlePointColor=(210, 250, 250), flags=0)
        return cv2.drawMatchesKnn(image1, keypoint1, image2, keypoint2, matches, matchesMask=matches_mask, **draw_params)

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
