# -*- coding: utf-8 -*-
from __future__ import division
import pickle
import numpy as np
from Filter import BPFilter
from CSP import CSPTrain, CSPSpatialFilter
from Classifier import ClassifierTrain
from CAR import CARFilter
import matplotlib.pyplot as plt
# from ODICA import ICAFunc


def TrainModel(train_x, train_y, classifier_type, m):
    """
       离线训练

       输入参数
       ----------
       train_x : T×N×L ndarray
                T: 采样点数  N: 通道数  L: 训练数据 epoch 总数
       train_y : L 训练数据 epoch 总数
       classifier_type: str 'svm' or 'lda'
       m: CSP 参数
       返回值
       ----------
       csp_ProjMatrix: 2m×N     CSP 投影矩阵
       classifier_model:  分类模型


    """
    # 带通滤波
    # AfterFilter_train_x = BPFilter(train_x, Fs, filter_low, filter_high)
    # CAR 滤波
    # AfterCAR_train_x = CARFilter(AfterFilter_train_x)
    # 去眼电R
    # AfterICA_train_x = ICAFunc(AfterFilter_train_x)
    # CSP 空间投影
    csp_ProjMatrix = CSPTrain(train_x, train_y, m)
    AfterCSP_train_x = CSPSpatialFilter(train_x, csp_ProjMatrix)
    # Classifier 分类模型
    classifier_model = ClassifierTrain(AfterCSP_train_x, train_y, classifier_type)

    return csp_ProjMatrix, classifier_model


if __name__ == '__main__':
    from loadData.loadnpz import loadnpz
    classifier_type = 'lda'
    m = 2
    filter_low = 8
    filter_high = 30
    train_x, train_y, Fs = loadnpz(
        'D:\\python\\PythonCodes\\PythonProjectsV2\\signal\\PL\\acquireNSsignal_2018_04_25_14_41_22.npz', filter_low, filter_high)
    # train_x1, train_y1, Fs1 = loadnpz(
    #     'D:\\python\\PythonCodes\\PythonProjectsV2\\signal\\ZQ\\onlineNSsignal_2018_04_25_14_48_06.npz', filter_low, filter_high)
    # train_x = np.concatenate((train_x, train_x1), axis=2)
    # train_y = np.concatenate((train_y, train_y1), axis=0)
    csp_ProjMatrix, classifier_model = TrainModel(train_x, train_y, classifier_type, m)
    f1 = open('D:\\python\\PythonCodes\\PythonProjectsV2\\signal\\PL\\TrainPL0426.pkl', 'wb')
    pickle.dump(csp_ProjMatrix, f1)
    pickle.dump(classifier_model, f1)
    f1.close()
