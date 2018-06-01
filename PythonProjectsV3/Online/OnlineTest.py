# -*- coding: utf-8 -*-
from __future__ import division
import scipy.io as sio
import numpy as np
import time
#import serial
from Filter import BPFilter
from CSP import CSPSpatialFilter
from Classifier import ClassifierPredict
from TrainModel import TrainModel
from CAR import CARFilter
import pickle


def OnlineTest(epoch, Fs, filter_low, filter_high, csp_ProjMatrix, classifier_model):
    """
       在线训练

       输入参数
       ----------
       epoch : T×N  单个epoch
                T: 采样点数  N: 通道数
       Fs : 采样率
       filter_low: 带通滤波低频范围
       filter_high: 带通滤波高频范围
       csp_ProjMatrix: 2m×N     CSP 投影矩阵
       classifier_model:  分类模型

       返回值
       ----------
       predict: ndarray(1,) double 分类结果

        """
    # try:
    #     t = serial.Serial('COM1', 9600)
    # except Exception as e:
    #     print('open serial failed.')

    # input = open('D:\Myfiles\WorkSpace\Codes\PythonProjects\model.pkl', 'rb')
    # csp_ProjMatrix = pickle.load(input)
    # classifier_model = pickle.load(input)
    # CAR
    epoch = CARFilter(epoch)
    AfterFilter_test_x = BPFilter(epoch, Fs, filter_low, filter_high)
    AfterCSP_test_x = CSPSpatialFilter(AfterFilter_test_x, csp_ProjMatrix)
    predict = ClassifierPredict(classifier_model, AfterCSP_test_x)

    # t.write(str(predict[0]))
    # time.sleep(1)
    # print predict, test_y[i]
    # t.close()
    return predict


if __name__ == '__main__':
    from loadData.loadnpz import loadnpz
    filter_low = 8
    filter_high = 30
    train_x, train_y, Fs = loadnpz('D:\\Myfiles\\EEGProject\\Neuroscan\\signals\\PanLi\\NSsignal_2018_04_10_19_34_41.npz', filter_low, filter_high)
    test_x, test_y, Fs = loadnpz('D:\\Myfiles\\EEGProject\\Neuroscan\\signals\\PanLi\\NSsignal_2018_04_10_19_19_01.npz', filter_low, filter_high)
    m = 3
    classifier_type = 'svm'
    csp_ProjMatrix, classifier_model = TrainModel(train_x, train_y, classifier_type, m)
    for i in range(10):
        epoch = test_x[:, :, i]
        predict = OnlineTest(epoch, Fs, filter_low, filter_high, csp_ProjMatrix, classifier_model)
        print(predict)
