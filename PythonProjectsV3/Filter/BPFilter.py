# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import scipy.signal as signal
def BPFilter(data_x, Fs, filter_low, filter_high):
    """
       IIR 带通滤波

       输入参数
       ----------
       data_x: T×N×L ndarray(或单个trial T×N)
               T: 采样点数  N: 通道数  L: 训练数据trial总数
           Fs: 采样频率

       返回值
       ----------
       AfterFilter_x: T×N×L(或单个trial T×N)

       """
    channel_num = data_x.shape[1]
    AfterFilter_x = np.zeros(data_x.shape)
    Wn1 = filter_low/(Fs/2)
    Wn2 = filter_high/(Fs/2)
    filter_order = 4
    b, a = signal.iirdesign([Wn1, Wn2], [Wn1-0.05, Wn2+0.05], 2, 40)
    # [b, a] = signal.butter(filter_order, [Wn1, Wn2], 'bandpass')
    # 输入为多个trial时
    if len(data_x.shape) == 3:
        trial_size = data_x.shape[2]
        for i in range(trial_size):
            for j in range(channel_num):
                AfterFilter_x[:, j, i] = signal.lfilter(b, a, data_x[:, j, i])
                # AfterFilter_x[:, j, i] = signal.filtfilt(b, a, data_x[:, j, i])

    # 输入为单个trial
    else:
        for j in range(channel_num):
            # AfterFilter_x[:, j] = signal.lfilter(b, a, data_x[:, j])
            AfterFilter_x[:, j] = signal.filtfilt(b, a, data_x[:, j])
    return AfterFilter_x
