#### General object classifier

![General object classifier](data/2019.09.25-general-object-classifier.png)

Watch [original video](https://youtu.be/CzPYgRaYWUA) of [Siraj Raval](https://sirajraval.com/) first.
And review the [original code](https://github.com/llSourcell/image_classifier_template)
of an image classification startup.

General object classifier is based on:
   * [Flutter](https://flutter.dev) mobile development framework with a single code base
     for Android and iOS applications;
   * [Python](https://www.python.org) for the deep learning web component;
   * [Firebase](https://firebase.google.com) for user authentication;
   * [Stripe](https://stripe.com) as the payment processor. 

and consists of five steps:
   1. Find an image dataset via [Google Dataset Search](https://toolbox.google.com/datasetsearch)
      or [Awesome Public Datasets](https://github.com/awesomedata/awesome-public-datasets) list.
      Also you can download images via [google_images_download](https://pypi.org/project/google_images_download)
      Python script or [Fatkun Batch Download Image add-on](https://chrome.google.com/webstore/detail/fatkun-batch-download-ima/nnjjahlikiabnchcpehcpkdeckfgnohf)
      for Chrome browser.
   2. Transfer learning. Take some trained model and retrain a part of it on your relatively small
      image dataset. To perform transfer learning install [fast.ai](https://www.fast.ai)
      vision library (version [1.0.57](https://pypi.org/project/fastai) or later).
      Fast.ai is built on top of [PyTorch](https://pytorch.org).
      During transfer training most weights of neural network are frozen in place
      except for the last layer. 
   3. Sign up for Firebase and Stride.
   4. Deploy the web app. Fast.ai made [this](https://github.com/render-examples/fastai-v3)
      impressively simple starter application for deploying fast.ai models on Render,
      for instantly creating a web app and API for your classifier.
   5. Build the mobile app. Connect your Flutter app to the web app from the previous step.

There are 3 components here:
   01. [model training script](01_training_script)
   02. [web API](02_web_api)
   03. [mobile app](03_mobile_app)

----
#### Step 1
Install [fastai](https://pypi.org/project/fastai/) if you need to train on your local computer:
```shell script
# Install PyTorch and Torchvision first, because fast.ai is built on top of PyTorch.
# Installation video - https://deeplizard.com/learn/video/UWlFM0R_x6I
# Be patient, it is 750.2 MB for now :-)
# For example: Stable 1.2 -> Windows -> Conda or pip -> Python 3.7 -> CUDA 10.0
pip3 install torch===1.2.0 torchvision===0.4.0 -f https://download.pytorch.org/whl/torch_stable.html
conda install pytorch torchvision cudatoolkit=10.0 -c pytorch
# Check it
pip list | grep torch
conda list torch

# PyPI Install
pip install fastai
# Conda Install
conda install fastai pytorch -c fastai -c pytorch -c conda-forge
conda install -c fastai fastai

# Check it
python -m fastai.utils.show_install
# Activate Anaconda environment and check it
conda activate
python -m fastai.utils.show_install
conda deactivate
```
Create your own directories with images to train or continue with existing
[bears classification](01_training_script).

----
#### Step 2
Run in [Jupyter Notebook](https://jupyter.org) file called
[`bear_classifier.ipynb`](01_training_script/bear_classifier.ipynb)
if you have computer **with modern GPU** or upload and run it in
[Google Colab](https://colab.research.google.com) if you do not have modern GPU.

Replace the bear dataset with your own image dataset.
Retrain a `resnet34` image classification model.
Such retraining is called transfer learning.

Save the resulting model `pkl` file to google drive, save the download link.

This is the original [`bear_classifier.ipynb`](https://github.com/naveenchanakya/bear-classifier/blob/master/bear_classifier.ipynb)
file of the [Bear Classifier](https://github.com/naveenchanakya/bear-classifier) project.

----
#### Step 3


----
#### Step 4


----
#### Step 5



P.S. There are some TensorFlow examples and links [here](https://github.com/foobar167/articles/tree/master/Machine_Learning)
and [here](https://github.com/foobar167/articles/blob/master/Ubuntu/13_Keras_and_TensorFlow_how-tos.md).
