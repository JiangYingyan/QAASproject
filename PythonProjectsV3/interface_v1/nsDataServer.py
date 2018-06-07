import socket
import struct
import time
import serial
import numpy as np
from pylsl import StreamInlet, resolve_stream
from DataServer import DataServer


class nsDataServer(DataServer):
    def __init__(self, parent):
        super(nsDataServer, self).__init__(parent)
        self.ip = 'localhost'
        self.port = 9889
        self.NSocket = socket.socket()
        self.NSocket.settimeout(15)
        self.signal = []

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
        if self.mainMenuData['exoskeletonFeedback']:  # — 连机械手Step 1 --
            comNum = self.mainMenuData['comNum']
            baudRate = 9600
            self.Com = self.ConnectToCOM(comNum, baudRate)
        self.SendCommandToNS(3, 5)
        time.sleep(0.1)
        # get basic information
        self.BasicInfo = self.NSocket.recv(100)
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
        self.SendCommandToNS(2, 1)
        self.SendCommandToNS(3, 3)

    def onDataRead(self):
        while (1):
            data_head = self.NSocket.recv(12)
            if (len(data_head) != 0):
                break
        # chId = str(data_head[0:4], encoding='utf-8')
        # Code = int.from_bytes(data_head[4:6], byteorder='big')
        # Request = int.from_bytes(data_head[6:8], byteorder='big')
        size = int.from_bytes(data_head[8:12], byteorder='big')
        total = 0
        Data = bytearray()

        while (total < size):
            a = self.NSocket.recv(size - total)
            Data = Data + a
            total = total + len(a)
        i = 0
        if(self.TimeOfsignal < 0):
            self.TimeOfsignal = time.clock()
            #print(time.time())
            print(self.TimeOfsignal)
        data = [i[0] * self.BResolution
                for i in struct.iter_unpack('<i', Data)]
        self.signalList += [data[i: i + self.channelNum]
                            for i in range(0, len(data), self.channelNum)]

        if self.markList[-1][1] == 769 and self.mainMenuData['exoskeletonFeedback']:
                self.SendEpochCommandToCom(self.Com, 1)
        if (self.markList[-1][1] == 770 or self.markList[-1][1] == 800) \
                and self.mainMenuData['exoskeletonFeedback']:
                self.SendEpochCommandToCom(self.Com, 0)
    def onDisconnect(self):
        self.SendCommandToNS(3, 4)
        self.SendCommandToNS(2, 2)
        self.SendCommandToNS(1, 2)
        if self.mainMenuData['exoskeletonFeedback']:  # — 连机械手Step 3 --
            self.Com.write('0'.encode())
            self.Com.close()

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

    def SendCommandToCom(self, com, result):
        com.write(str(result).encode())

    def SendCommandToNS(self, ctrcode, reqnum):
        a = 'CTRL'
        Cmd = a.encode(encoding="utf-8")
        Cmd += (ctrcode).to_bytes(2, 'big')
        Cmd += (reqnum).to_bytes(2, 'big')
        Cmd += (0).to_bytes(4, 'big')
        self.NSocket.sendall(Cmd)

    def getSignal(self):
        return np.array(self.signal)

    def loadSettings(self, mainMenuData):
        self.mainMenuData = mainMenuData

    def saveData(self, path):
        self.TimeOfsignal = np.array([self.TimeOfsignal])
        self.mark = np.array(self.markList)
        self.signal = np.array(self.signalList)
        np.savez(time.strftime(path + "\\acquireNSsignal_%Y_%m_%d_%H_%M_%S"),
                 signal=self.signal, mark=self.mark, timestamp=self.timestamp, firstsignal = self.TimeOfsignal)

