import socket
import struct
import time
import pickle
import numpy as np
import sys
sys.path.append("E:\MIproject\PythonProjectV3")
from Online import OnlineTest
from DataServer import DataServer
from StimulationsCodes import *
import serial



class neDataServer(DataServer):
    def __init__(self, parent):
        super(neDataServer, self).__init__(parent)
        self.ip = 'localhost'
        self.port = 1234
        self.NSocket = socket.socket()
        self.NSocket.settimeout(15)
        self.signal = []
        self.channelNum = 8
        #self.T = self.BlockPnts / self.BSampleRate / 2
        self.sampleRate = 500
        self.signalList = []
        self.epochsize = 20*8*4

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
        # comNum = 17
        # baudRate = 115200
        # self.Com = self.ConnectToCOM(comNum, baudRate)
        # -------------------------------

    def onDataRead(self):
        if(self.connected == True):
            total = 0
            Data = bytearray()
            while (total < self.epochsize):
                a = self.NSocket.recv(self.epochsize - total)
                Data = Data + a
                total = total + len(a)
            data = [i[0]
                    for i in struct.iter_unpack('<i', Data)]
            self.signalList += [data[i: i + self.channelNum]
                                for i in range(0, len(data), self.channelNum)]
            if self.markList[len(self.markList) - 1][1] == 770 or self.markList[len(self.markList) - 1][1] == 769 or \
                    self.markList[len(self.markList) - 1][1] == 781:
                OnlineSignal = np.array(self.signalList[len(self.signalList) - 500: len(self.signalList)])
                onlineS = OnlineSignal[:, 0:self.BEegChannelNum]
                # onlineS = np.delete(onlineS, 6, 1)  # Cz 打通了 移除 = =
                predict = OnlineTest(onlineS, self.BSampleRate, 8, 30, self.csp_ProjMatrix,
                                     self.classifier_model)

                self.OnlineResult.append(int(predict))
                # self.SendEpochCommandToCom(self.Com, predict)  # 不连机械手注释2 ver2 exoskeleton
            if len(self.OnlineResult) != 0 and self.markList[len(self.markList) - 1][1] == 800:
                i = 20
                # left = right = 0
                # while(i < len(self.OnlineResult)):
                # if(self.OnlineResult[i] == 0):
                #     left = left + 1
                # elif(self.OnlineResult[i] == 1):
                #     right = right + 1
                # i = i + 1
                right = sum(self.OnlineResult[i:])
                left = len(self.OnlineResult) - i - right
                print('————————————')

                if left < right:  # if(right > 1/3 *(right + left)):
                    if self.markList[len(self.markList) - 3][1] == 770:
                        self.rightcount = self.rightcount + 1
                    print('classification result; right |cue:' + str(self.markList[len(self.markList) - 3][1]))
                    # SendTrialCommandToCom(self, com, 0) # 不连机械手注释2 ver1 exoskeleton
                else:
                    if self.markList[len(self.markList) - 3][1] == 769:
                        self.rightcount = self.rightcount + 1
                    print('classification result; left |cue:' + str(self.markList[len(self.markList) - 3][1]))
                    # SendTrialCommandToCom(self, com, 1) # 不连机械手注释2 ver1 exoskeleton
                result_str = 'left count:' + str(left) + ', right count:' + str(right)
                print(result_str)
                print('rightcount:' + str(self.rightcount))
                self.OnlineResult = []


    def onDisconnect(self):
        self.NSocket.close()
    def getSignal(self):
        return np.array(self.signal)

    def saveData(self, path):
        self.TimeOfsignal = np.array([self.TimeOfsignal])
        self.mark = np.array(self.markList)
        self.signal = np.array(self.signalList)
        np.savez(time.strftime(path + "\\acquireNSsignal_%Y_%m_%d_%H_%M_%S"),
                 signal=self.signal, mark=self.mark, timestamp=self.timestamp,firstsignal = self.TimeOfsignal)