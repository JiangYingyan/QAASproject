# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from .CARFilter import CARFilter
from loadData.loadov import loadov
# trainx = sio.loadmat(r'D:\Myfiles\WorkSpace\Codes\PythonProjects\Data\trainx.mat')
# train_x = trainx['train_x']  # shape(750,22,60)
train_x, train_y1 = loadov("D:\\Myfiles\\openvibefiles\\MI-CSP-r1\\signals\\GH\\GH-171225-acquisition-3.mat")
data_x = CARFilter(train_x)
# np.linspace(start, stop, num)指定的间隔内返回均匀间隔的数字
t = np.linspace(1, data_x.shape[0], data_x.shape[0])
plt.figure(1)
plt.subplot(211)
# plt.plot(t[0:400], train_x[0:400, 3, 2])
plt.plot(t, train_x[:, 0, 1])
plt.subplot(212)
# plt.plot(t[0:400], data_x[0:400, 3, 2])
plt.plot(t, data_x[:, 0, 1])
plt.show()
