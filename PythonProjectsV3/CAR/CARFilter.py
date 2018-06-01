# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np


def CARFilter(data_x):
    """
       common average referencing filter 共均值参考滤波

       输入参数
       ----------
       data_x: T×N×L ndarray(或单个trial T×N)
               T: 采样点数  N: 通道数  L: 训练数据trial总数

       返回值
       ----------
       AfterCAR_data_x: CAR后的数据

       """
    channel_num = data_x.shape[1]
    afterCAR_data_x = np.zeros(data_x.shape)
    if len(data_x.shape) == 3:
        trial_size = data_x.shape[2]
        for j in range(trial_size):
            channel_sum = np.zeros(data_x.shape[0])
            for i in range(channel_num):
                channel_sum = channel_sum + data_x[:, i, j]
            channel_mean = channel_sum / channel_num
            for i in range(channel_num):
                afterCAR_data_x[:, i, j] = data_x[:, i, j] - channel_mean
    else:
        channel_sum = np.zeros(data_x.shape[0])
        for i in range(channel_num):
            channel_sum = channel_sum + data_x[:, i]
        channel_mean = channel_sum / channel_num
        for i in range(channel_num):
            afterCAR_data_x[:, i] = data_x[:, i] - channel_mean

    return afterCAR_data_x
