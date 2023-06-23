#### Bear Classifier

Original [`bear_classifier.ipynb`](https://github.com/naveenchanakya/bear-classifier/blob/master/bear_classifier.ipynb)
file of the [Bear Classifier](https://github.com/naveenchanakya/bear-classifier) project.

Create dataset using google images and classify between teddy bear,
grizzly bear and black bear using Pytorch and fastai.

Run in [Jupyter Notebook](https://jupyter.org) file called
[`bear_classifier.ipynb`](01_training_script/bear_classifier.ipynb)
if you have computer **with modern GPU** or upload and run it in
[Google Colab](https://colab.research.google.com/drive/1pFSa6Bf2ddJe_ZdJBr9uQOANLRbsRwaf)
if you do not have modern GPU.

Replace the bear dataset with your own image dataset.
Retrain a `resnet34` image classification model.
Such retraining is called transfer learning.

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

Shared link with the [`bear_classifier.ipynb`](https://colab.research.google.com/drive/1pFSa6Bf2ddJe_ZdJBr9uQOANLRbsRwaf)
script.
