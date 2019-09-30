#### Bear Classifier

Original [`bear_classifier.ipynb`](https://github.com/naveenchanakya/bear-classifier/blob/master/bear_classifier.ipynb)
file of the [Bear Classifier](https://github.com/naveenchanakya/bear-classifier) project.

Create our own dataset using google images and classify between teddy bear,
grizzly bear and black bear using Pytorch and fastai.

Run [Jupyter Notebook](https://jupyter.org) called
[`bear_classifier.ipynb`](bear_classifier.ipynb)
on your local machine with modern GPU or upload and run it to
[Google Colab](https://colab.research.google.com) if you not have modern GPU.

Replace the bear dataset with your own image dataset.
It's retraining a `resnet34` image classification model. This is transfer learning.

Save the resulting model `pkl` file to google drive, save the download link.

List of URLs to download the respective class images:
   * [blackbear.txt](urls/blackbear.txt)
   * [grizzlybear.txt](urls/grizzlybear.txt)
   * [teddybear.txt](urls/teddybear.txt)

To start transfer learning on the local computer (you need modern GPU for it):
```shell script
# Install additional packages
pip install jupyter
# Run it
jupyter notebook
# Or run it via Google Colab
```
