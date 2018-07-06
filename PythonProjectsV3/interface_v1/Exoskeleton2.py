# -*- coding: utf-8 -*-

#控制系外骨骼控制，各个函数作用参考Exoskeleton.py
import socket

class Exoskeleton:
    def __int__(self):
        print('link to exoskeleton')
#为机械手建立服务端，等待机械臂连接
    def LinkToExoskleton(self, ip, port):
        ip = "localhost"
        port = 12234
        self.ESocket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip, port)
        self.ESocket1.bind(server_address)
        print('wait for exoskeleton connect,starting listen on localhost, 12234')
        self.connected = False
        try:
            self.ESocket1.listen(1)
        except socket.error as e:
            print("fail to listen on port " )
        addr = None
        while(not addr):
            self.ESocket,addr = self.ESocket1.accept()
        self.connected = True
        print("connect to exoskeleton successfully")
        self.CommandNumber = None

    def SendHeadCommandToCom(self, speed, startangle, endangle):
            print('Initial Setting Successfully')

    def ExoskeletonMove(self):
        print('move')
        self.ESocket.sendall('move'.encode())


    def ExoskeletonStop(self):
        print('stop')
        self.ESocket.sendall('rest'.encode())


    def StrategyTiral(self,command):
        if(command == 'move'):
            self.ExoskeletonMove()
        if(command == 'rest'):
            self.ExoskeletonStop()

    def StrategyEpoch(self,command):
        if(not self.CommandNumber):
            self.CommandNumber = 0
            self.LastCommand = 'rest'
            self.EpochCommand = ['rest', 'rest', 'rest']

        self.EpochCommand[self.CommandNumber % len(self.EpochCommand)] = command
        print(self.EpochCommand)
        self.CommandNumber = self.CommandNumber + 1
        movenumber = self.EpochCommand.count('move')
        restnumber = self.EpochCommand.count('rest')
        if(movenumber == len(self.EpochCommand) and self.LastCommand == 'rest'):
            self.ExoskeletonMove()
            self.LastCommand = 'move'
        elif(restnumber == len(self.EpochCommand) and self.LastCommand == 'move'):
            self.ExoskeletonStop()
            self.LastCommand = 'rest'

    def Disconnected(self):
        self.ExoskeletonStop()
        self.ESocket.close()

if __name__ == "__main__":
    # 测试外骨骼指令策略(模拟Epoch分类结果)
    import time
    ES = Exoskeleton()
    comNum = 'localhost'
    baudRate = 5566
    ES.LinkToExoskleton(comNum, baudRate)
    time.sleep(2)
    ES.SendHeadCommandToCom(30, 1700, 2200)
    testlist = ['move', 'move', 'move', 'move', 'rest', 'rest','rest','rest','move', 'move', 'move']
    for i in range(len(testlist)):
        ES.StrategyEpoch(testlist[i])
        time.sleep(2)
    ES.ExoskeletonStop()
    time.sleep(2)
    ES.Disconnected()