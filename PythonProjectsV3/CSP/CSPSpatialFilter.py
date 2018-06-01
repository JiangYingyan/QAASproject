# -*- coding: utf-8 -*-
import numpy as np


def CSPSpatialFilter(data_x, csp_ProjMatrix):
    """
       返回 CSP 空间滤波后的数据

       输入参数
       ----------
       data_x: T×N×L ndarray(或单个trial T×N)
               T: 采样点数  N: 通道数  L: 训练数据trial总数
       csp_ProjMatrix: 2m×N
               CSP 投影矩阵

       返回值
       ----------
       xAfterCSP: L×2m (或单个trial 1D 2m)  空间滤波后的数据

       """

    feature_len = csp_ProjMatrix.shape[0]
    if len(data_x.shape) == 3:
        trial_size = data_x.shape[2]
        xAfterCSP = np.zeros([trial_size, feature_len])
        for i in range(trial_size):
            Z = np.dot(csp_ProjMatrix, np.transpose(data_x[:, :, i]))  # 1个trial脑电信号投影后得到Z(2m×T)
            feature = np.log((Z.var(1)/(Z.var(1)).sum()).transpose())  # feature: 2m
            xAfterCSP[i, :] = feature
    else:
        Z = np.dot(csp_ProjMatrix, np.transpose(data_x))  # 1个trial脑电信号投影后得到Z(2m×T)
        feature = np.log((Z.var(1) / (Z.var(1)).sum()).transpose())  # feature: 2m
        xAfterCSP = np.zeros([1, feature_len])
        xAfterCSP[0, :] = feature
    return xAfterCSP
