# -*- coding: utf-8 -*-
import socket
import struct
import time
import pickle
import numpy as np
from Online import OnlineTest
from DataServer import DataServer
from StimulationsCodes import *
import serial

class OnlinensDataServer(DataServer):
    def __init__(self, parent):
        super(OnlinensDataServer, self).__init__(parent)
        self.ip = 'localhost'
        self.port = 9889
        self.NSocket = socket.socket()
        self.NSocket.settimeout(15)
        self.predictList = np.zeros(3)  # 实时指令
        self.lastCommand = 0  # 记忆上一条指令
        self.signal = []
        self.Com = None

    def onConnect(self):
        try:
            self.NSocket.connect((self.ip, self.port))

        except Exception as e:
            print(e.strerror)
            print("Data Server Connection Failed")
            self.connected = False
            return
        else:
            print("Data Server Connection Completed")
            self.NSocket.settimeout(None)
            self.connected = True
        # --不连机械手注释1 exoskeleton--
        comNum = 18
        baudRate = 9600
        try:
            self.Com = self.ConnectToCOM(comNum, baudRate)
        except Exception as e:
            print(str(e))
        # -------------------------------
        self.SendCommandToNS(3, 5)
        time.sleep(0.1)
        # get basic information
        self.BasicInfo = self.NSocket.recv(100)

        #self.stimcount = 0
        ID = str(self.BasicInfo[0:4], encoding='utf-8')
        Code = int.from_bytes(self.BasicInfo[4:6], byteorder='big')
        req = int.from_bytes(self.BasicInfo[6:8], byteorder='big')
        size = int.from_bytes(self.BasicInfo[8:12], byteorder='big')
        if(Code == 1 and
           req == 3 and
           size == 28 and
           len(self.BasicInfo) == 40):
            self.Bsize = int.from_bytes(
                self.BasicInfo[12:16], byteorder='little')
            self.BEegChannelNum = int.from_bytes(
                self.BasicInfo[16:20], byteorder='little')
            self.BEventChannelNum = int.from_bytes(
                self.BasicInfo[20:24], byteorder='little')
            self.BlockPnts = int.from_bytes(
                self.BasicInfo[24:28], byteorder='little')
            self.BSampleRate = int.from_bytes(
                self.BasicInfo[28:32], byteorder='little')
            self.BDataSize = int.from_bytes(
                self.BasicInfo[32:36], byteorder='little')
            self.BResolution = struct.unpack('<f', self.BasicInfo[36:40])[0]
            self.channelNum = self.BEegChannelNum + self.BEventChannelNum
            self.T = self.BlockPnts / self.BSampleRate / 2
            self.sampleRate = self.BSampleRate
            self.signalList = []
            self.rightcount = 0
            self.OnlineResult = []


        self.SendCommandToNS(2, 1)
        self.SendCommandToNS(3, 3)
        # input = open('D:\\python\\PythonCodes\\PythonProjectsV2\\signal\\PL\\TrainPL0426.pkl', 'rb')
        # self.classifier_model = pickle.load(input)
        # self.csp_ProjMatrix = pickle.load(input)


    def onDataRead(self):
        while(1):
            data_head = self.NSocket.recv(12)
            if (len(data_head) != 0):
                break
        chId = str(data_head[0:4], encoding='utf-8')
        Code = int.from_bytes(data_head[4:6], byteorder='big')
        Request = int.from_bytes(data_head[6:8], byteorder='big')
        size = int.from_bytes(data_head[8:12], byteorder='big')
        total = 0
        Data = bytearray()

        while (total < size):
            a = self.NSocket.recv(size - total)
            Data = Data + a
            total = total + len(a)
        i = 0
        if self.TimeOfsignal < 0:
            self.TimeOfsignal = time.clock()
            print(self.TimeOfsignal)
        data = [i[0] * self.BResolution
                for i in struct.iter_unpack('<i', Data)]
        self.signalList += [data[i: i + self.channelNum]
                            for i in range(0, len(data), self.channelNum)]
        if self.markList[-1][1] == 770 or self.markList[-1][1] == 769 or self.markList[-1][1] == 781:
            OnlineSignal = np.array(self.signalList[-500:])
            onlineS = OnlineSignal[:, 0:self.BEegChannelNum]
            predict = OnlineTest(onlineS, self.BSampleRate, 8, 30, self.csp_ProjMatrix,
                                    self.classifier_model)

            self.OnlineResult.append(int(predict))

            self.SendEpochCommandToCom(self.Com, predict)  # 不连机械手注释2 ver2 exoskeleton

        if len(self.OnlineResult) != 0 and self.markList[-1][1] == 800:
            self.Com.write('0'.encode())
            i = 20
            left = right = 0
            while(i < len(self.OnlineResult)):
                if(self.OnlineResult[i] == 0):
                    left = left + 1
                elif(self.OnlineResult[i] == 1):
                    right = right + 1
                i = i + 1
            # right = sum(self.OnlineResult[i:])
            # left = len(self.OnlineResult) - i - right
            print('————————————')

            if left < right:  # if(right > 1/3 *(right + left)):
                if self.markList[len(self.markList) - 3][1] == 770:
                    self.rightcount = self.rightcount + 1
                print('classification result; right |cue:' + str(self.markList[len(self.markList)-3][1]))
                # SendTrialCommandToCom(self, com, 0) # 不连机械手注释2 ver1 exoskeleton
            else:
                if self.markList[len(self.markList) - 3][1] == 769:
                    self.rightcount = self.rightcount + 1
                print('classification result; left |cue:' + str(self.markList[len(self.markList)-3][1]))
                # SendTrialCommandToCom(self, com, 1) # 不连机械手注释2 ver1 exoskeleton
            result_str = 'left count:' + str(left) + ', right count:' + str(right)
            print(result_str)
            print('rightcount:' + str(self.rightcount))
            self.OnlineResult = []

    def onDisconnect(self):
        self.SendCommandToNS(3, 4)
        self.SendCommandToNS(2, 2)
        self.SendCommandToNS(1, 2)
        self.Com.write('0'.encode())
        self.Com.close()  # 不连机械手注释3 exoskeleton

    def SendCommandToNS(self, ctrcode, reqnum):
        a = 'CTRL'
        Cmd = a.encode(encoding="utf-8")
        Cmd += (ctrcode).to_bytes(2, 'big')
        Cmd += (reqnum).to_bytes(2, 'big')
        Cmd += (0).to_bytes(4, 'big')
        self.NSocket.sendall(Cmd)

    def getSignal(self):
        return np.array(self.signal)

    def saveData(self, path):
        self.TimeOfsignal = np.array([self.TimeOfsignal])
        self.mark = np.array(self.markList)
        self.signal = np.array(self.signalList)
        np.savez(time.strftime(path + "\\onlineNSsignal_%Y_%m_%d_%H_%M_%S"),
                 signal=self.signal, mark=self.mark, timestamp=self.timestamp, firstsignal=self.TimeOfsignal)

    def ConnectToCOM(self, comNum, baudRate):
        print('Connecting to COM')
        com_name = 'COM' + str(comNum)
        COM = None
        try:
            COM = serial.Serial(com_name, baudRate)
            print('Connect to COM successfully')
        except Exception as e:
            print('Open serial failed. '+str(e))
        return COM

    def SendTrialCommandToCom(self, com, result):
        com.write(str(result))

    def SendEpochCommandToCom(self, com, predict):
        self.predictList[:-1] = self.predictList[1:]
        self.predictList[-1] = predict
        # 全1 且未输出过 动的指令
        if sum(self.predictList) == len(self.predictList) and self.lastCommand != 0:
            self.lastCommand = 0
            #self.lastCommand.encode('ascii')
            # print("0___")
            com.write('0'.encode())
        elif sum(self.predictList) == 0 and self.lastCommand != 1:
            self.lastCommand = 1
            # print("1___")
            #com.write(str(self.lastCommand))
            com.write('1'.encode())

    def loadTrainModel(self, pklPath):
        # input = open('D:\\python\\PythonCodes\\PythonProjectsV2\\signal\\PL\\TrainPL0426.pkl', 'rb')
        input = open(pklPath, 'rb')
        # self.csp_ProjMatrix = pickle.load(input)
        self.classifier_model = pickle.load(input)
        self.csp_ProjMatrix = pickle.load(input)


if __name__ == "__main__":
    # 测试外骨骼指令策略(模拟Epoch分类结果)
    import random
    import time
    dataServer = OnlinensDataServer(DataServer)
    comNum = 18
    baudRate = 9600
    predictList = np.zeros(3)
    Com = dataServer.ConnectToCOM(comNum, baudRate)
    for i in range(500):
        #Com.write('1'.encode())
        predict = random.randint(0, 1)
        print(str(predict))
        dataServer.SendEpochCommandToCom(Com, predict)
        time.sleep(0.04)
    Com.write('0'.encode())
    Com.close()

