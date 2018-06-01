# -*- coding: utf-8 -*-
# import mne
import matplotlib.pyplot as plt
# from CSP.Montage import *
from CSP.channelPos import channelPos


def CSPPatternsPlot(csp_ProjMatrix, channels):
    """
       返回 CSP 空间滤波后的数据

       输入参数
       ----------
       csp_ProjMatrix: ndarray, shape(n_components, n_channels)) 2m×N
                       CSP 投影矩阵 即空间模式


       返回值
       ----------


       """
    data = csp_ProjMatrix[[0, -1], :]

    n_components = data.shape[0]
    pos = channelPos(channels)
    # pos = Montage(channels).get_pos()
    fig, axes = plt.subplots(1, n_components)
    # for idx in range(n_components):
        # mne.viz.plot_topomap(data[idx, :], pos, axes=axes[idx], show=False)
    fig.suptitle('CSP patterns')
    fig.tight_layout()
    fig.show()


if __name__ == "__main__":
    import scipy.io as sio
    from CSP.CSPTrain import CSPTrain
    from CSP.CSPSpatialFilter import CSPSpatialFilter
    m = 3  # CSP 参数
    # 竞赛数据
    trainx = sio.loadmat(r'D:\Myfiles\PythonProjects\Data\trainx.mat')
    trainy = sio.loadmat(r'D:\Myfiles\PythonProjects\Data\trainy.mat')
    train_x = trainx['train_x']  # shape(750,22,60)
    train_y = trainy['train_y']  # shape(1,60)
    # neuroscan 数据
    from loadData.loadnpz import loadnpz
    classifier_type = 'lda'
    filter_low = 8
    filter_high = 30
    # train_x, train_y, Fs = loadnpz(
    #     'D:\\Myfiles\\PythonProjects\\signal\\ZJJ\\0423\\acquireNSsignal_2018_04_23_15_36_14.npz', filter_low, filter_high)
    channels22 = ['fz', 'fc3', 'fc1', 'fcz', 'fc2', 'fc4', 'c5', 'c3', 'c1', 'cz', 'c2', 'c4', 'c6',
                    'cp3', 'cp1', 'cpz', 'cp2', 'cp4', 'p1', 'pz', 'p2', 'poz']
    channels14 = ['cz', 'c2', 'f3', 'fz', 'f4', 'c3', 'c4', 'c1', 'fcz', 'fc1', 'fc2', 'cp3', 'cp4', 'cpz']
    channels8 = ['f3', 'fz', 'f4', 'fc1', 'fc2', 'c3', 'cz', 'c4']
    csp_ProjMatrix = CSPTrain(train_x, train_y.ravel(), m)
    fig = CSPPatternsPlot(csp_ProjMatrix[:, :], channels22)

