import serial

class Exoskeleton:
    def __int__(self):
        print('link to exoskeleton')
        self.EpochCommand = ['rest', 'rest', 'rest']
        self.LastCommand = 'rest'
        self.CommandNumber = 0
    def LinkToExoskleton(self, comNum, baudRate):
        print('Trying to Connect to COM')
        com_name = 'COM' + str(comNum)
        self.COM = None
        try:
            self.COM = serial.Serial(com_name, baudRate)
            print('Connect to COM successfully')
        except Exception as e:
            print('Open serial failed.' + str(e))

        self.CommandNumber = None
    def SendHeadCommandToCom(self, speed, startangle, endangle):
        Command = 'C' + str(speed) + 'A'+str(startangle) + 'B'+str(endangle)
        self.COM.write(Command.encode())
        print('Initial Setting Successfully')

    def ExoskeletonMove(self):
       # print('move')
        self.COM.write('1'.encode())

    def ExoskeletonStop(self):
        #print('stop')
        self.COM.write('0'.encode())

    def StrategyTiral(self,command):
        if(command == 'move'):
            self.ExoskeletonMove()
        if(command == 'rest'):
            self.ExoskeletonStop()

    def StrategyEpoch(self,command):
        if(not self.CommandNumber):
            self.CommandNumber == 0
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




