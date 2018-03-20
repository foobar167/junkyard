from distutils.core import setup, Extension
from numpy.distutils.misc_util import get_numpy_include_dirs

setup(name         = "Co-occurrence matrix",
      version      = "1.0",
      ext_modules  = [Extension("comatrix", ["comatrix.c"])],
      include_dirs = get_numpy_include_dirs())
