# Introduction
This is the source code of our TCSVT 2019 paper "Fast Fine-grained Image Classification via Weakly Supervised Discriminative Localization , Please cite the following paper if you use our code.

Xiangteng He, Yuxin Peng and Junjie Zhao, "Fast Fine-grained Image Classification via Weakly Supervised Discriminative Localization", IEEE Transactions on Circuits and Systems for Video Technology (TCSVT), Vol. 29, No. 5, pp. 1394-1407, May. 2019.

# Dependency
Our code is based on early version of [Faster R-CNN in MXNet](https://github.com/precedenceguo/mx-rcnn), all the dependencies are the same as it.

# Data Preparation
Here we use Cars-196 dataset for an example, we have organized the data as the form of PASCAL VOC dataset, which can be downloaded from [link](https://pan.baidu.com/s/1C4-HkqLaZvteymzvkMp1fA).

Download VGG16 pretrained model vgg16-0000.params from [MXNet model gallery](https://github.com/dmlc/mxnet-model-gallery/blob/master/imagenet-1k-vgg.md) to model folder.

# Usage
Start training and tesing by executiving the following commands. This will train and test the network on Cars-196 train. 

    - sh train_end2end_cam_prepare.sh
    - python train_end2end_cam.py --gpu GPUID
    - python test.py --gpu GPUID
    - sh train_end2end_conv5_prepare.sh
    - python train_end2end_conv5.py --gpu GPUID
    - python test.py --gpu GPUID
    - sh train_end2end_conv4_prepare.sh
    - python train_end2end_conv4.py --gpu GPUID
    - python test.py --gpu GPUID
Download the models that we trained from the [link](https://pan.baidu.com/s/1yiUxbzUoFeD5bRdkMWRVPw) and unzipped to ./model/ foldes. For more information, please refer to our [TCSVT paper](https://ieeexplore.ieee.org/document/8356107/).

Welcome to our [Laboratory Homepage](http://www.icst.pku.edu.cn/mipl/home/) for more information about our papers, source codes, and datasets.
