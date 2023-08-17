#### OpenCV feature detector and descriptor extractor

![Under construction](../data/2019.09.25-under-construction-icon.png)

**Under construction...**

![Snapshot from application](./data/snapshot.jpg)

Objects tracking using feature extraction algorithms with GUI
for tests and education. 

Snapshots, logs and configuration parameters are saved in `temp` directory
of this folder.
Used **only** OpenCV integrated detectors, descriptors and
detector-descriptors. Neural Network detector-descriptors (such as
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
In general the source code of the GUI is not as elegant as I would like, but it works :-).

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

Software architecture:
`architecture diagram`

[MS PowerPoint presentation](./data/2023.07.25-presentation-opencv-descriptos.pptx)
of the application in the `data` directory.
