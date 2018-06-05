import socket
import struct
import time

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