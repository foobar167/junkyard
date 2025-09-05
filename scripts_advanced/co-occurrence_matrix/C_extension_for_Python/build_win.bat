rm -fr build
rm -f comatrix.pyd
c:\programs\Python27\python.exe setup.py build_ext --inplace
c:\programs\Python27\python.exe test.py
