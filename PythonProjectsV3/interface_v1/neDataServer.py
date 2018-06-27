import socket
import struct
import time
import serial
import numpy as np
from pylsl import StreamInlet, resolve_stream
from DataServer import DataServer

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
        if self.parent.mainMenuData['exoskeletonFeedback']:  # — 连机械手Step 1 --
            comNum = self.parent.mainMenuData['comNum']
            baudRate = 9600
            self.Com = self.ConnectToCOM(comNum, baudRate)
            # 配置角度范围、速度
            angleStart = self.parent.mainMenuData['angleStart']
            self.angleStart = int(1600 + angleStart /360 * 4096)  # 初始位置
            angleRange = self.parent.mainMenuData['angleRange']
            self.angleRange = int(angleRange / 360 * 4096)  # 范围
            self.angleEnd = self.angleStart + self.angleRange  # 结束位置
            self.velocity = self.parent.mainMenuData['velocity']
            self.SendHeadCommandToCom(self.Com, self.velocity, self.angleStart, self.angleEnd)
            self.Handmove = 0

    def onDataRead(self):
        if(self.connected == True):
            total = 0
            Data = bytearray()
            while (total < self.epochsize):
                a = self.NSocket.recv(self.epochsize - total)
                Data = Data + a
                total = total + len(a)
            data = [i[0]
                    for i in struct.iter_unpack('>i', Data)]
            self.signalList += [data[i: i + self.channelNum]
                                for i in range(0, len(data), self.channelNum)]
            if (self.TimeOfsignal < 0):
                self.TimeOfsignal = time.clock()
                # print(time.time())
                print(self.TimeOfsignal)

            if self.markList[-1][1] == 769 and self.parent.mainMenuData['exoskeletonFeedback'] and self.Handmove == 0:
                self.Com.write('1'.encode())
                print('handmove')
                self.Handmove = 1
            if (self.markList[-1][1] == 770 or self.markList[-1][1] == 800) \
                    and self.parent.mainMenuData['exoskeletonFeedback'] and self.Handmove == 1:
                self.Com.write('0'.encode())
                print('handstop')
                self.Handmove = 0


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

    def SendHeadCommandToCom(self, com, speed, startangle, endangle):
        Command = 'C' + str(speed) + 'A' + str(startangle) + 'B' + str(endangle)
        com.write(Command.encode())
        print(Command)
       # time.sleep(0.5)
        #com.write('1'.encode())
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
