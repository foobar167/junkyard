#### Object tracking

Object tracking using OpenCV
*feature detectors* (detectors) and *descriptor extractors* (descriptors)
algorithms with GUI for fun, tests and education. 

![Snapshot from application](./data/snapshot.jpg)

**Only** OpenCV integrated detectors, descriptors and
detector-descriptors are used. Neural Network detector-descriptors (such as
R2D2, D2NET, SUPERPOINT, ORB-SLAM2, DELF, CONTEXTDESC, LFNET, KEYNET, DISK,
[etc](https://github.com/luigifreda/pyslam/blob/master/feature_types.py))
and descriptors (such as TFEAT, HARDNET, GEODESC, SOSNET, L2NET, LOGPOLAR,
[etc](https://github.com/luigifreda/pyslam/blob/master/feature_types.py))
are not considered.
All object trackers in the application are placed in *decrease of efficiency* and
implemented *rotation invariant* and *scalable* except of “StarDetector + DAISY”
for education and fun. It doesn't mean that lower methods are always ineffective,
but for this task it is so (because there is no "silver bullet" method for all tasks).
All feature detector-descriptor logic is in the
[logic_extractor.py](./extractor/logic_extractor.py) file.
Snapshots, logs and configuration parameters are saved in `temp` directory
of this folder.
In general the source code of the GUI is not as elegant as I would like, but it works :-).

Previous simple script is here
[SIFT object tracking](simple_scripts/sift_tracking.py).
SIFT algorithm became free since March 2020.
SURF algorithm is patented and is excluded from OpenCV.
Now SURF is for Python version 3.4.2.16 and older.

Tested on **Windows 10** for Python **3.11**.

External libraries:
   * **OpenCV** to process images.
   * **NumPy** to support arrays.
   * **Pillow** to open images of [various formats](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).

To start:
```shell
# Install additional libraries
pip install -r requirements.txt
# Run the application
python runme.py
```

Usage:
  1. Open GUI: `python runme.py`.
  2. Place object in front of the web camera, so it take all visible space.
  3. Press `Get snapshot` button. Application will make snapshot of the object to track.
  4. After taking snapshot there will be a red rectangle around tracking object
and green lines connecting special keypoints of the image.

Rectangular object, like book, is tracked better than face.

[MS PowerPoint presentation](./data/2023.07.25-presentation-opencv-descriptos.pptx)
of the application in the `data` subdirectory.
