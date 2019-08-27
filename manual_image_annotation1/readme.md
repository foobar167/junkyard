##### Manual image annotation with polygons

![Manual image annotation with polygons](../data/2019.01.03-manual-image-annotation-with-polygons.png)

Manual image annotation opens image where user can select
polygon areas around the objects of interest.

After selecting region of interest user presses menu button
and program cuts rectangular images from selected polygons
with a scanning window.

Parameters of the scanning window are set in the
configuration INI file which is in the "Temp" directory.

The output of the program is the set of rectangular
images from the polygon areas in the "Temp"
directory.

To start Manual Image Annotation with polygons:
```shell
c:\path\to\your\python\version-3.x\python.exe runme.py
```

Tested on Windows and Ubuntu for Python 3.7.

External libraries:
```shell
Pillow
```

Software architecture:
![Software architecture](../data/2019.06.17-annotation-with-polygons-architecture.png)
