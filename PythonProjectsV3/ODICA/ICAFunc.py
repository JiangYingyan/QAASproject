# -*- coding: utf-8 -*-
import numpy as np
from sklearn.decomposition import PCA, FastICA
from ADJBP import ADJBP

def ICAFunc(data_x):
    """
       OD-ICA去眼电

       输入参数
       ----------
       data_x : T×N×L ndarray
                T: 采样点数  N: 通道数  L: 训练数据trial总数

       返回值
       ----------
       AfterICA_data_x: T×N×L ndarray
                       T: 采样点数  N: 通道数  L: 训练数据trial总数

       """
    trial_size = data_x.shape[2]
    AfterICA_data_x = np.zeros(data_x.shape)
    for i in range(trial_size):
        AfterICA_data_x[:, :, i] = ICASingleTrial(data_x[:, :, i])
    return AfterICA_data_x



def ICASingleTrial(X):
    """
       OD-ICA 单个trial样本数据 去眼电

       输入参数
       ----------
       X : T 采样点 x N 通道数

       返回值
       ----------
       reconSetZero: T 采样点 x N 通道数

       """
    # pca = PCA()
    pca_w = PCA(whiten=True)
    ica = FastICA()

    # fit_transform
    # X: array - like, shape(n_samples, n_features)
    # returns: array-like, shape (n_samples, n_components)

    # PCAsig = pca.fit_transform(X)
    PCAsig_W = pca_w.fit_transform(X)
    ICAsig = ica.fit_transform(PCAsig_W)

    setZero = np.zeros(ICAsig.shape)
    for i in range(ICAsig.shape[1]):
        isOutlier = ADJBP(ICAsig[:,i])
        vector = ICAsig[:,i]  # 取矩阵的列
        vector[isOutlier] = 0
        setZero[:,i] = vector

    reconSetZero = pca_w.inverse_transform(ica.inverse_transform(setZero))

    return reconSetZero
