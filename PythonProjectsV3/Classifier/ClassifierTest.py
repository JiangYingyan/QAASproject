# -*- coding: utf-8 -*-
from __future__ import division
import scipy.io as sio
import numpy as np
from .ClassifierTrain import ClassifierTrain
from .ClassifierPredict import ClassifierPredict
dataForClassification = sio.loadmat(r'D:\Myfiles\WorkSpace\Codes\PythonProjects\Data\dataForClassification.mat')
train_x = dataForClassification['train_x'] # shape(60,6)
train_y = dataForClassification['train_y'] # shape(60,1)
test_x = dataForClassification['test_x'] # shape(78,6)
test_y = dataForClassification['test_y'] # shape(78,1)
predict_y = dataForClassification['predict_y'] # shape(78,1)
model = ClassifierTrain(train_x, train_y.ravel(), 'svm')#y.ravel()将2D(shapes, 1)改成1D(shapes, )的形式
predict = ClassifierPredict(model, test_x)
t = (predict == np.transpose(test_y))
right = sum(map(sum,t))
Accuracy = right/test_y.size
print('正确率:', str(Accuracy))
