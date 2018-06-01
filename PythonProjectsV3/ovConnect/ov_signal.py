# -*- coding: utf-8 -*-
import numpy as np
import sys
import pickle
sys.path.append("D:\python\PythonCodes\PythonProjectsV3")
from TrainModel import TrainModel
from Filter import BPFilter
from CAR import CARFilter


# let's define a new box class that inherits from OVBox
class MyOVBox(OVBox):
    def __init__(self):
        OVBox.__init__(self)
        # we add a new member to save the signal header information we will receive
        self.signalHeader = None
        # self.signal_trial = None
        self.signal_label = None
        self.signal_stim = None
        self.signal_start = None
        self.signal_latest = None
        self.a = None
        self.trained = False
    # this time we also re-define the initialize method to directly prepare the header and the first data chunk
    # 初始化
    def initialize(self):
        print('Initializing Python Box')
        self.signal_label = []
        self.signal_trial = []
        self.signal_stim = []
        self.output[0].append(OVStimulationHeader(0., 0.))

    # The process method will be called by openvibe on every clock tick
    #  循环调用
    def process(self):
        chunkNum = len(self.input[0])
        if self.signal_latest != None and chunkNum == 0 and self.getCurrentTime() - self.signal_latest > 10:
            self.appendStopStimulation()
        # we iterate over all the input chunks in the input signal buffer 遍历输入信号缓冲区中的所有输入块
        for chunkIndex in range(chunkNum):
            chunk = self.input[0].pop()
            if (type(chunk) == OVSignalHeader):
                self.signalHeader = chunk
                self.signal_start = chunk.startTime
                self.signal = np.empty(shape=[self.signalHeader.dimensionSizes[0], 0])
                print('Data chunk size:' + str(self.signalHeader.dimensionSizes))
            # if it's a buffer we pop it and put it in a numpy array at the right dimensions
            elif (type(chunk) == OVSignalBuffer):
                npBuffer = np.array(chunk).reshape(
                    tuple(self.signalHeader.dimensionSizes))
                self.signal = np.concatenate((self.signal, npBuffer), axis=1)
            # if it's a end-of-stream we just forward that information to the output
            elif (type(chunk) == OVSignalEnd):
                print('Data Read Finished')
            self.signal_latest = self.getCurrentTime()


        for stimIndex in range(len(self.input[1])):
            stim = self.input[1].pop()
            if (type(stim) != OVStimulationHeader):
                for i in range(len(stim)):
                    if (stim[i].identifier == 32770):
                        self.train()
						# Call data process function. Data in var signal
                        self.trained = True
                        self.appendStopStimulation()
                    else:
						self.signal_stim.append((stim[i].identifier,stim[i].date,stim[i].duration))


        # this time we also re-define the uninitialize method to output the end chunk.
    def uninitialize(self):
        if (self.trained == False):
            self.train()
        end = self.getCurrentTime()
        # self.output[0].append(OVStimulationEnd(end, end))
        # print('Size of signal: ' + str(len(self.signal_trial)))
        # print(str(self.signal_trial[12].shape) + str(self.signal_trial[13].shape))
        self.output[0].append(OVStimulationEnd(end, end))
        print(self.signal_label)
        print('Uninitializing Python Box')

    def appendStopStimulation(self):
        stimSet = OVStimulationSet(self.getCurrentTime(), self.getCurrentTime() + 1. / self.getClock())
        stimSet.append(OVStimulation(0x00008207, self.getCurrentTime(), 0))
        self.output[0].append(stimSet)

    def train(self):
		# TODO: Signal Epoching base on Stimulation
		# Using signal_start, signal, singal_stim[id,date,duration] in self

        trialsize = 0
        for stim in self.signal_stim:
            if stim[0] == 769 or stim[0] == 770:
                trialsize = trialsize + 1
        print("trial_size:"+str(trialsize))
        Fs = self.signalHeader.samplingRate

        filter_low = 8
        filter_high = 30
        # self.signal.shape: channal x sample
        Data = CARFilter(np.transpose(self.signal))  # CAR
        Data = BPFilter(Data, Fs, filter_low, filter_high)  # 带通滤波
        # print('signal:' + str(self.signal.shape))
        # print('Data:'+str(Data.shape[1]))
        # 滑窗
        width = 2500  # 单个trial 的总长
        step = 100  # 步长
        window_size = 500  # 窗的大小
        delay = 0  # cue 出现后延迟
        window_num = int((width - delay - window_size) / step + 1)  # 每个trial 滑多少个窗
        j = 0
        # signal_label = np.zeros(trialsize * window_num)
        channal_num = Data.shape[1]
        signal3d = np.zeros([window_size, channal_num, trialsize * window_num])
        for stim in self.signal_stim:
            if stim[0] == 769 or stim[0] == 770:
                pos = int((stim[1] - self.signal_start) / (1.0 / Fs))
                for i in range(window_num):
                    # signal_label[j] = stim[0] - 769
                    self.signal_label.append(stim[0] - 769)
                    start = int(pos + i * step + delay)
                    signal3d[:, :, j] = Data[start:start + window_size, :]
                    j = j + 1
        print(str(signal3d.shape))
        classifier_type = 'lda'
        m = 2
        csp_ProjMatrix, classifier_model = TrainModel(signal3d, self.signal_label, classifier_type, m)
        output = open('D:\python\PythonCodes\PythonProjectsV3\signals\ov_model\model.pkl', 'wb')
        pickle.dump(csp_ProjMatrix, output)
        pickle.dump(classifier_model, output)
        output.close()
        print('CSP: ' + str(csp_ProjMatrix.shape))


# Finally, we notify openvibe that the box instance 'box' is now an instance of MyOVBox.
# Don't forget that step !!
box = MyOVBox()
