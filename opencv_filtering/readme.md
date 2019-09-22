##### OpenCV Filtering GUI application

![OpenCV Filtering GUI](data/2019.09.04-opencv-filtering-gui.png)

OpenCV Filtering GUI is a set of various realtime filters to process
images from the webcam.

Tested on **Windows** and **Ubuntu** for Python **3.7.4** amd OpenCV **3.4.2.16**.

Why OpenCV version **3.4.2.16** and not newer?
Because it seems that SIRF and SURF are
[no longer available in opencv > 3.4.2.16](https://github.com/DynaSlum/satsense/issues/13).
If you need SIRF and SURF algorithms use OpenCV 3.4.2.16 or older.

External libraries:
```shell
opencv-contrib-python==3.4.2.16  # OpenCV 3.4.2.16 with contributions
pillow  # PIL package for image processing
numpy   # NumPy support for arrays and matrices

# Installation
pip install opencv-contrib-python==3.4.2.16 pillow numpy
```

Run command:
```shell
c:\path\to\python\version-3.x\python.exe runme.py
```

Software architecture:
![Software architecture](data/2019.09.04-opencv-filtering-architecture.png)
