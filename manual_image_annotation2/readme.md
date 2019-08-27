##### Manual image annotation with rectangles

![Manual image annotation with rectangles](../data/2019.01.03-manual-image-annotation-with-rectangles.png)

Manual image annotation creates rectangular images with selected
areas of interest (ROI). User opens image and selects rectangular
areas of interest.

After selecting rectangles and pressing menu button program cuts
rectangle images from the bigger image.

All parameters are saved in configuration INI files
which is in the "Temp" directory.

The output of the program is the set of rectangular images
in the "Temp" directory.

To start Manual Image Annotation with rectangles:
```shell
c:\path\to\your\python\version-3.x\python.exe runme.py
```

Tested on Windows and Ubuntu for Python 3.7.

External libraries:
```shell
Pillow
```

Software architecture:
![Software architecture](../data/2019.06.17-annotation-with-rectangles-architecture.png)
