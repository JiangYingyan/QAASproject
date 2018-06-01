# -*- coding: utf-8 -*-
import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing

def loadov(path):
    """
       读NE生成的ov转mat文件，生成滑窗后数据

       输入参数
       ----------
       filepath: npz文件路径

       返回值
       ----------
       signal3d: T×N×L ndarray
                 T: 采样点数  N: 通道数  L: 训练数据trial总数
       signal_label: shape (n_samples,)
                L 个trial对应的标签


       """
    data = sio.loadmat(path)
    Fs = data['samplingFreq']  # 采样 500Hz
    data_x = data['samples']  # 数据
    data_x_time = data['sampleTime']
    data_x_time = data_x_time[:, 0].tolist()
    stims = data['stims']  # 标签[time; ID; duration] (10个769,10个770)

    # 确定 769/770 cue 出现位置
    label = []
    label_time= []
    trialsize = 0
    for i in range(stims.shape[0]):
        if stims[i, 1] == 769 or stims[i, 1] == 770:
            trialsize = trialsize + 1
            label.append(stims[i, 1]-769)
            label_time.append(stims[i, 0])
    pos = []
    for i in range(len(label_time)):
        for j in range(len(data_x_time)):
            if data_x_time[j] > label_time[i]:
                pos.append(j)
                break


    # 滑窗
    width = 2500  # 单个trial 的总长
    step = 50  # 步长
    window_size = 500  # 窗的大小
    delay = 500  # cue 出现后延迟
    window_num = int((width - delay - window_size) / step + 1)  # 每个trial 滑多少个窗
    j = 0
    signal_label = np.zeros(trialsize * window_num)
    channal_num = Data.shape[1]
    signal3d = np.zeros([window_size, channal_num, trialsize * window_num])
    for k in range(len(label)):
        for i in range(window_num):
            signal_label[j] = label[k]
            start = int(pos[k] + i * step + delay)
            signal3d[:, :, j] = Data[start:start + window_size, :]
            j = j + 1


    # data_x = reduceModerate(signal3d, signal_label)
    data_x = normalizeDatax(signal3d)

    # t = np.linspace(1, data_x.shape[0], data_x.shape[0])
    # plt.figure(1)
    # plt.subplot(211)
    # # plt.plot(t[0:400], train_x[0:400, 3, 2])
    # plt.plot(t, data_x[:, 2, 30])
    # plt.subplot(212)
    # # plt.plot(t[0:400], data_x[0:400, 3, 2])
    # plt.plot(t, data_x[:, 3, 30])
    # plt.show()

    return data_x, signal_label


def reduceModerate(signal3d, signal_label):
    # 减静息态均值
    data_x = np.zeros(signal3d.shape)
    samples = signal3d.shape[0]
    sum = np.zeros(signal3d.shape[1])
    for i in range(len(signal_label)):
        if signal_label[i] == 1:
            for j in range(samples):
                sum = sum + signal3d[j, :, i]
            mean = sum / samples
            break
        else:
            continue
    for i in range(len(signal_label)):
        for j in range(samples):
            data_x[j, :, i] = signal3d[j, :, i] - np.transpose(mean)
    return data_x

def normalizeDatax(signal3d):
    # 归一化
    data_x = np.zeros(signal3d.shape)
    channal_num = signal3d.shape[1]
    for i in range(signal3d.shape[2]):
        for j in range(channal_num):
            data_x[:, j, i] = preprocessing.scale(signal3d[:, j, i])
    return data_x


if __name__ == "__main__":
    Data, label = loadov('D:\Myfiles\openvibefiles\MI-CSP-r1\signals\GH\GH-171225-online-1.mat')