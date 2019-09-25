##### General object classifier

![General object classifier](data/2019.09.25-general-object-classifier.png)

Watch [original video](https://youtu.be/CzPYgRaYWUA) of [Siraj Raval](https://sirajraval.com/) first.
And review the [original code](https://github.com/llSourcell/image_classifier_template).

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

P.S. There are some TensorFlow examples and links [here](https://github.com/foobar167/articles/tree/master/Machine_Learning)
and [here](https://github.com/foobar167/articles/blob/master/Ubuntu/13_Keras_and_TensorFlow_how-tos.md).
