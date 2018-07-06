# -*- coding: utf-8 -*-

#香港理工机械手控制
import serial
class Exoskeleton:
    def __int__(self):

        self.CommandNumber = 0
    #连接串口，输入串口号和波特率
    def LinkToExoskleton(self, comNum, baudRate):
        print('Trying to Connect to COM')
        com_name = 'COM' + str(comNum)
        self.COM = None
        try:
            self.COM = serial.Serial(com_name, baudRate)
            print('Connect to COM successfully')
        except Exception as e:
            print('Open serial failed.' + str(e))
        print('link to exoskeleton')
        self.CommandNumber = None

    #初始化 输入外骨骼的运动速度，运动起始角度和结束角度
    def SendHeadCommandToCom(self, speed, startangle, endangle):
        Command = 'C' + str(speed) + 'A'+str(startangle) + 'B'+str(endangle)
        self.COM.write(Command.encode())
        print('Initial Setting Successfully')
#给串口发送动指令
    def ExoskeletonMove(self):
        print('move')
        self.COM.write('1'.encode())
#给串口发送停止指令
    def ExoskeletonStop(self):
        print('stop')
        self.COM.write('0'.encode())
#按每个tiral执行命令
    def StrategyTiral(self,command):
        if(command == 'move'):
            self.ExoskeletonMove()
        if(command == 'rest'):
            self.ExoskeletonStop()
#按每个epoch执行命令
    def StrategyEpoch(self,command):
        if (not self.CommandNumber):
            self.LastCommand = 'rest'
            self.CommandNumber = 0
            self.EpochCommand = ['rest', 'rest', 'rest']

        self.EpochCommand[self.CommandNumber % len(self.EpochCommand)] = command
        #print(self.EpochCommand)
        self.CommandNumber = self.CommandNumber + 1
        movenumber = self.EpochCommand.count('move')
        restnumber = self.EpochCommand.count('rest')
        if(movenumber == len(self.EpochCommand) and self.LastCommand == 'rest'):
            self.ExoskeletonMove()
            self.LastCommand = 'move'
        elif(restnumber == len(self.EpochCommand) and self.LastCommand == 'move'):
            self.ExoskeletonStop()
            self.LastCommand = 'rest'
#关闭串口
    def Disconnected(self):
        self.ExoskeletonStop()
        self.COM.close()


if __name__ == "__main__":
    # 测试外骨骼指令策略(模拟Epoch分类结果)
    import time
    ES = Exoskeleton()
    comNum = 17
    baudRate = 9600
    ES.LinkToExoskleton(comNum, baudRate)
    ES.SendHeadCommandToCom(30, 1700, 2200)
    testlist = ['move', 'move', 'move', 'move', 'rest', 'rest','rest','rest','move', 'move', 'move']
    for i in range(len(testlist)):
        ES.StrategyEpoch(testlist[i])
        time.sleep(1.5)
    ES.ExoskeletonStop()
    time.sleep(2)
    ES.Disconnected()




