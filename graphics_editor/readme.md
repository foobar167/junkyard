#### Simple Python graphics editor

![Under construction](../data/2019.09.25-under-construction-icon.png)

**Under construction...**

Simple Python graphics editor with minimal external
3rd party libraries.

... `some explanations should be here`

After drawing rectangles and pressing menu button program cuts
rectangle images from the bigger image.

All parameters are saved in configuration INI file `config.ini`,
which is in the `temp` directory.

The output of the application is the set of rectangular images
in the `temp` directory. No concept of the image project
is implemented yet, so all new files are placed
in the `temp` subdirectory.

It saves rectangular areas for the image in TXT format
as a [pickle object](https://realpython.com/python-pickle-module/).
You could open saved areas, modify them and cut image again.

Tested on **Windows** for Python **3.7**.

External libraries:
   * **Pillow** to open images of [various formats](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).

To start Manual Image Annotation with rectangles:
```shell
# Install additional packages
pip install pillow
# Run it
python runme.py
```

Software architecture:
`architecture diagram`
