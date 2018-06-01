import sched
import threading
from time import monotonic, sleep, clock, strftime
import time
import numpy as np


class DataServer:
    def __init__(self, parent):
        self.setParent(parent)
        self.sche = sched.scheduler()
        self.sche.enter(0, 1, self.onSched)
        self.thread = threading.Thread(target=self.sche.run)
        self.connected = False
        self.sampleRate = 500
        self.samplePeriod = 0.002
        self.signal = np.empty(0)
        self.signalList = []
        self.mark = np.empty(0)
        self.markList = []
        self.timestamp = np.empty(0)
        self.timestampList = []
        self.setReady()
        self.setProcess()
        self.setFinish()
        self.TimeOfsignal = -1

    def setParent(self, parent):
        self.parent = parent
        # self.parent.setDataServer(self)

    def onSched(self):
        now = monotonic()
        self.sche.enterabs(now+self.T, 1, self.onSched)
        try:
            self.onDataRead()
        except Exception as e:
            print(str(e))
        self.endTime = clock()
        self.onProcess(self)
        self.timestamp = np.concatenate(
            (self.timestamp, np.arange(self.endTime)))

    def configure(self, frez=16):
        self.T = 1.0/frez

    def start(self):
        self.onConnect()
        if(self.connected):
            print('Data Server Ready')
        self.onReady(self)
        self.startTime = clock()
        #print(time.time())
        self.thread.start()

    def stop(self):
        self.onFinish(self)
        if self.connected:
            self.onDisconnect()
        print('Data Server Disconnected')
        for i in self.sche.queue:
            self.sche.cancel(i)
        self.thread.join()

    def onConnect(self):
        pass

    def onDataRead(self):
        pass

    def onDisconnect(self):
        pass

    def onStim(self, stim):
        self.markList.append(
            [stim['timestamp'], stim['code'], stim['duration']])

    def setReady(self, func=lambda x: None):
        self.onReady = func

    def setProcess(self, func=lambda x: None):
        self.onProcess = func

    def setFinish(self, func=lambda x: None):
        self.onFinish = func

    def setSampleRate(self, rate):
        self.sampleRate = rate
        self.samplePeriod = 1.0/rate

    def setSamplePeriod(self, period):
        self.samplePeriod = period
        self.sampleRate = int(1.0/period)

    def saveData(self, path):
        self.TimeOfsignal = np.array([self.TimeOfsignal])
        self.mark = np.array(self.markList)
        self.signal = np.array(self.signalList)
        np.savez(strftime("signal_%Y_%m_%d_%H_%M_%S"),
                 signal=self.signal, mark=self.mark, timestamp=self.timestamp, firstsignal=self.TimeOfsignal)
