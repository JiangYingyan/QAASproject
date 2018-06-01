# -*- coding: utf-8 -*-
import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
from .BPFilter import BPFilter
data_xForFilter = sio.loadmat(r'D:\Myfiles\WorkSpace\Codes\PythonProjects\Data\data_xForFilter.mat')
data_x = data_xForFilter['data_x']  # shape(750,22,138)
Fs = 250
filter_low = 8
filter_high = 30
AfterFilter_x = BPFilter(data_x, Fs, filter_low, filter_high)
plt.subplot(121)
t = np.linspace(1, data_x.shape[0], data_x.shape[0])
plt.plot(t, data_x[:, 1, 1])
plt.subplot(122)
plt.plot(t, AfterFilter_x[:, 1, 1])
plt.show()
