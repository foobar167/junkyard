## Python collection of tests, probes, hacks and ideas

<!--
![Under construction](data/2019.09.25-under-construction-icon.png)
**Under construction...**
-->

   01. [LLM experiments](#llm_experiments)
   01. [Coral TPU](#coral_tpu)
   01. [PyTorch Tutorial](#pytorch_tutorial)
   01. [Object tracking](#feature_extractor)
   01. [Python notes and links to interesting places](#python_notes)
   01. [Image Processing with Python](#image_processing)
   01. [General object classifier](#object_classifier)
   01. [OpenCV Filtering GUI](#opencv_filtering)
   01. [Sending emails with Python](#send_email)
   01. [Manual image annotation with polygons](#manual_annotation1)
   01. [Manual image annotation with rectangles](#manual_annotation2)
   01. [Image viewer](#image_viewer)
   01. [Advanced zoom](#zoom)
   01. [**C** extension for Python](#c_extension)
   01. [OpenCV + Tkinter snapshot GUI](#opencv_tkinter)
   01. [OpenCV features](#opencv_features)
   01. [Multilanguage for Python](#multilanguage)
   01. [Dynamic menu](#dynamic_menu)</li>
   01. [Rolling window on NumPy arrays](#rolling_window)
   01. [Tkinter progressbar](#progressbar)


----------------
### <a name="llm_experiments" />[LLM experiments](llm_experiments)

Large Language Models Experiments.

----------------
### <a name="coral_tpu" />[Coral TPU](coral_tpu)

Python scripts for Google Coral USB Accelerator.

<img src="coral_tpu/pictures/google-coral-usb-accelerator.jpg" alt="Google Coral USB Accelerator" width="300" />

----------------
### <a name="pytorch_tutorial" />[PyTorch Tutorial](pytorch_tutorial)
PyTorch tutorial with [Aladdin Persson](https://www.youtube.com/@AladdinPersson/playlists)
in Google CoLab.
In this folder are Jupyter `*.ipynb` copies.
Here is the [online CoLab](https://drive.google.com/drive/folders/1z6dXh0qPMzgPKAwAjm1KFD0-P31Ds9Er)
replica of [this](https://www.youtube.com/playlist?list=PLhhyoLH6IjfxeoooqP9rhU3HJIAVAJ3Vz)
original course.

![Aladdin Persson logo](data/logo_aladdin_persson.jpg)

----------------
### <a name="feature_extractor" />[Object tracking](feature_extractor)
Object tracking using OpenCV
*feature detectors* (detectors) and *descriptor extractors* (descriptors)
algorithms with GUI for fun, tests and education. 

![Snapshot from application](feature_extractor/data/snapshot.jpg)

Previous simple script is here
[SIFT object tracking](simple_scripts/sift_tracking.py).
SIFT algorithm became free since March 2020.

----------------
### <a name="python_notes" />[Python notes and links to interesting places](notes_and_links.md)
Bookmarks to remember and re-visit.

----------------
### <a name="image_processing" />Image Processing with Python
[My replica](https://colab.research.google.com/drive/1M6j5FyqwQtAe85RtbOXkqjQldY8eoT7a)
of this original course: [Image Processing with Python](https://datacarpentry.org/image-processing/).

![Image Processing with Python](data/2019.12.03_dice_contours.jpg)

----------------
### <a name="object_classifier" />[General object classifier](object_classifier)
Classifies 3 types of bears: bronw, black and teddy bear.

![Bear classifier](object_classifier/03_mobile_app/data/2019.10.04_bear_classifier-2.jpg)

Object classifier is based on:
   * [Python](https://www.python.org) and [fast.ai](https://www.fast.ai)
     for model training through deep learning;
   * [Render](https://render.com) cloud provider to deploy your code in web.
   * [Flutter](https://flutter.dev) mobile development framework with a single code base
     for Android and iOS applications;
   * [Firebase](https://firebase.google.com) for Google Analytics.

And consists of 3 components:
  01. [model training script](object_classifier/01_training_script) - 
      Jupyter (Colab) script to train a classification model.
  02. [web app](https://github.com/foobar167/web_api_for_render) -
      starter project to deploy a trained classification model to the web.
  03. [mobile app](object_classifier/03_mobile_app) -
      mobile application which connect your web app with mobile phone (tested for Android).

----------------
### <a name="opencv_filtering" />[OpenCV Filtering GUI](opencv_filtering)
OpenCV Filtering GUI is a set of various realtime filters
to process images from the webcam.
This GUI is based on the previous [OpenCV features](#opencv_features) demo with
enhanced Tkinter controls for user-friendly OpenCV real-time filters demonstration.

![OpenCV Filtering GUI](opencv_filtering/data/2019.09.29-opencv-filtering-gui.png)

----------------
### <a name="send_email" />[Sending emails with Python](send_email)
Sending emails with Python.

![Sending emails with Python](data/2019.12.27_gmail_python.jpg)

----------------
### <a name="manual_annotation1" />[Manual image annotation with polygons](manual_image_annotation1)
Manual image annotation opens image where user can select polygon areas
around the objects of interest. After selecting region of interest user
presses menu button and program cuts rectangular images from selected
polygons with a scanning window.

![Manual image annotation with polygons](
manual_image_annotation1/data/2019.01.03-manual-image-annotation-with-polygons.png)

----------------
### <a name="manual_annotation2" />[Manual image annotation with rectangles](manual_image_annotation2)
Manual image annotation creates rectangular images with selected
areas of interest (ROI). User opens image and selects rectangular
areas of interest. After selecting rectangles and pressing menu button
program cuts rectangle images from the bigger image.

![Manual image annotation with rectangles](
manual_image_annotation2/data/2019.01.03-manual-image-annotation-with-rectangles.png)

----------------
### <a name="image_viewer" />[Image viewer](image_viewer)
Image viewer shows image and prints coordinates of the rectangular area in the console.

![Image viewer](image_viewer/data/2019.01.03-image-viewer.png)

----------------
### <a name="zoom" />[Advanced zoom](zoom_advanced3.py)
Advanced zoom for images of various formats and sizes
from small to huge up to several GB.

![Advanced zoom](data/2019.01.03-advanced-zoom.png)

----------------
### <a name="c_extension" />[**C** extension for Python](co-occurrence_matrix/C_extension_for_Python)
_**C**_ language extension for Python language by example of
co-occurrence matrix calculation.

----------------
### <a name="opencv_tkinter" />[OpenCV + Tkinter snapshot GUI](opencv_tkinter.py)
Take shapshot using webcamera, OpenCV and Tkinter.
Example is well documented and has many comments inside.

![OpenCV + Tkinter snapshot GUI](data/2019.01.03-opencv-tkinter.png)

----------------
### <a name="opencv_features" />[OpenCV features](camera_features.py)
Demo of various OpenCV features.
Application is tested for Windows OS and requires webcam.
There is a [newer version with GUI](opencv_filtering).

![OpenCV features](data/2019.01.03-opencv-features.png)

----------------
### <a name="multilanguage" />[Multilanguage for Python](translation)
How-to implement multilanguage for Python.

----------------
### <a name="dynamic_menu" />[Dynamic menu](dynamic_menu.py)
Example of the dynamic menu for Tkinter GUI.

----------------
### <a name="rolling_window" />[Rolling window on NumPy arrays](simple_scripts/rolling_window_on_NumPy_arrays.ipynb)
General examples for 1D, 2D, 3D and MD rolling window arrays in the on-line
[CoLab notebook](https://colab.research.google.com/drive/1Zru_-zzbtylgitbwxbi0eDBNhwr8qYl6).

It has zero Python cycles inside, so the speed is the same as in **C** programming language.

![Rolling window on NumPy arrays](data/2020.02.24-rolling-window-3d.png)

My previous examples of the rolling window for 2D array are
[here](rolling_window_advanced.py) and [here](rolling_window.py).

----------------
### <a name="progressbar" />[Tkinter progressbar](tkinter_progressbar.py)
Example of the Tkinter progressbar GUI.

![Tkinter progressbar](data/2019.01.03-tkinter-progressbar.png)
