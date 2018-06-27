import wx
import pickle
from Graz import Graz, MIStimulator
from nsDataServer import nsDataServer
from neDataServer import neDataServer
from OnlinensDataServer import OnlinensDataServer
from OnlineneDataServer import OnlineneDataServer


class acqAndTrainModelWindow(wx.Dialog):
    def __init__(self, parent, title):
        super(acqAndTrainModelWindow, self).__init__(parent, title=title, size=(615, 360))
        self.Centre()
        panel = wx.Panel(self)

        dataWildcard = "npz Data File (.npz)" + "|*.npz"

        # Accquisition Session box
        sbox1 = wx.StaticBox(panel, -1, label=u'校准阶段')
        self.sbsizer1 = wx.StaticBoxSizer(sbox1, wx.VERTICAL)
        gridSizer1 = wx.FlexGridSizer(cols=3, vgap=10, hgap=1)

        self.accquDataPath = wx.DirPickerCtrl(panel, size=(327, 27))
        self.accquDataPath.GetPickerCtrl().SetLabel('浏览')
        label = wx.StaticText(panel)
        label.SetLabel("校准数据存储路径：")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer1.Add(self.accquDataPath, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.AccStartBtn = wx.Button(panel, label="开始校准任务", size=wx.Size(100, 27))
        self.AccStartBtn.Bind(wx.EVT_BUTTON, self.OnAcqStart)
        gridSizer1.Add(self.AccStartBtn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.sbsizer1.Add(gridSizer1, proportion=0, flag=wx.ALL, border=5)

        # Train Model box
        sbox2 = wx.StaticBox(panel, -1, label=u'模型训练')
        self.sbsizer2 = wx.StaticBoxSizer(sbox2, wx.VERTICAL)
        gridSizer2 = wx.FlexGridSizer(cols=3, vgap=10, hgap=1)

        self.TrainDataPath = wx.FilePickerCtrl(panel, wildcard=dataWildcard, size=(350, 27))
        self.TrainDataPath.GetPickerCtrl().SetLabel('浏览')
        label = wx.StaticText(panel)
        label.SetLabel("选择训练数据：")
        gridSizer2.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer2.Add(self.TrainDataPath, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.statusLabel = wx.StaticText(panel)
        self.statusLabel.SetLabel("")
        gridSizer2.Add(self.statusLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.TrainModelPath = wx.DirPickerCtrl(panel, size=(350, 27))
        self.TrainModelPath.GetPickerCtrl().SetLabel('浏览')
        label = wx.StaticText(panel)
        label.SetLabel("模型存储路径：")
        gridSizer2.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer2.Add(self.TrainModelPath, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.TrainModelBtn = wx.Button(panel, label="模型训练开始", size=wx.Size(100, 27))
        self.TrainModelBtn.Bind(wx.EVT_BUTTON, self.OnTrainModel)
        gridSizer2.Add(self.TrainModelBtn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.sbsizer2.Add(gridSizer2, proportion=0, flag=wx.ALL, border=5)

        self.backBtn = wx.Button(panel, label="返回", size=(100, 27))
        self.backBtn.Bind(wx.EVT_BUTTON, self.OnBack)

        gridSizer = wx.FlexGridSizer(cols=1, vgap=1, hgap=1)
        gridSizer.Add(self.backBtn, 0, wx.ALL, 5)
        gridSizer.Add(self.sbsizer1, 0, wx.ALL, 5)
        gridSizer.Add(self.sbsizer2, 0, wx.ALL, 5)
        panel.SetSizerAndFit(gridSizer)
        panel.Center()
        self.Fit()

    def OnBack(self, event):
        self.Close()  # 关闭窗体

    def OnAcqStart(self, event):
        firstClassNum = self.CueSettingData['firstClassNum']
        secondClassNum = self.CueSettingData['secondClassNum']
        baseline = self.CueSettingData['baselineDuration']
        waitCue = self.CueSettingData['waitCueDuration']
        dispCue = self.CueSettingData['dispCueDuration']
        customFirstCuePath = self.CueSettingData['customFirstClass']
        customSecondCuePath = self.CueSettingData['customSecondClass']
        auditoryCue = self.CueSettingData['auditoryIsChecked']
        self.DataPath = self.accquDataPath.GetPath()
        self.graz = Graz(self, customFirstCuePath, customSecondCuePath, auditoryCue)
        self.stim = MIStimulator(self.graz,
                                 first_class='OVTK_GDF_Left',
                                 number_of_first_class=firstClassNum,
                                 second_class='OVTK_GDF_Right',
                                 number_of_second_class=secondClassNum,
                                 baseline_duration=baseline,
                                 wait_for_cue_duration=waitCue,
                                 display_cue_duration=dispCue,
                                 )
        self.dataServer = nsDataServer(self)
        #self.dataServer = neDataServer(self)
        msg = "总时长: " + str(self.stim.T)+"秒\n"+"是否开始任务?"
        style = wx.OK | wx.CANCEL | wx.CENTRE
        msgbox = wx.MessageDialog(self, msg, "校准任务开始", style)
        if(msgbox.ShowModal() == wx.ID_OK):
            self.graz.Show()
            self.graz.startStim()
            if self.dataServer:
                self.dataServer.configure()
                if(not self.dataServer.connected):
                    self.dataServer.start()
        else:
            return

    def OnTrainModel(self, event):
        from loadData.loadnpz import loadnpz
        from TrainModel import TrainModel
        import time
        TrainDataPath = self.TrainDataPath.GetPath()
        TrainModelPath = self.TrainModelPath.GetPath()
        classifier_type = 'lda'
        m = 3
        filter_low = 8
        filter_high = 30
        train_x, train_y, Fs = loadnpz(TrainDataPath, filter_low, filter_high)
        # train_x1, train_y1, Fs1 = loadnpz(
        #     'D:\\python\\PythonCodes\\PythonProjectsV2\\signal\\ZQ\\onlineNSsignal_2018_04_25_14_48_06.npz', filter_low, filter_high)
        # train_x = np.concatenate((train_x, train_x1), axis=2)
        # train_y = np.concatenate((train_y, train_y1), axis=0)
        csp_ProjMatrix, classifier_model = TrainModel(train_x, train_y, classifier_type, m)
        TrainModelPath = time.strftime(TrainModelPath + "\\TrainModel_%Y_%m_%d_%H_%M_%S.pkl")
        f1 = open(TrainModelPath, 'wb')

        pickle.dump(csp_ProjMatrix, f1)
        pickle.dump(classifier_model, f1)
        f1.close()
        self.statusLabel.SetLabel('模型训练完成。')

    # Acquisition 传入cue设置与主窗体设置数据
    def setValue(self, CueSettingData, mainMenuData):
        self.CueSettingData = CueSettingData
        self.mainMenuData = mainMenuData

    # Acquisition 关闭窗体时返回数据给主窗体
    def getValue(self):
        acqAndTrainModelData = {
            'accquDataPath': self.accquDataPath.GetPath(),
            'TrainDataPath': self.TrainDataPath.GetPath(),
            'TrainModelPath': self.TrainModelPath.GetPath()
        }
        return acqAndTrainModelData

    # Acquisition 加载初始化数据
    def initData(self, acqAndTrainModelData):
        self.accquDataPath.SetPath(acqAndTrainModelData['accquDataPath'])
        self.TrainDataPath.SetPath(acqAndTrainModelData['TrainDataPath'])
        self.TrainModelPath.SetPath(acqAndTrainModelData['TrainModelPath'])

    def grazFinish(self):
        if self.dataServer:
            self.dataServer.stop()
            print('Saving Signal...')
            path = self.DataPath
            self.dataServer.saveData(path)
            print('Signal Saved')

class OnlineTestWindow(wx.Dialog):
    def __init__(self, parent, title):
        super(OnlineTestWindow, self).__init__(parent, title=title, size=(615, 280))
        self.Centre()
        panel = wx.Panel(self)
        TrainModelWildcard = "pkl Data File (.pkl)" + "|*.pkl"

        # Online Test box
        sbox1 = wx.StaticBox(panel, -1, label=u'训练阶段')
        self.sbsizer1 = wx.StaticBoxSizer(sbox1, wx.VERTICAL)
        gridSizer1 = wx.FlexGridSizer(cols=3, vgap=10, hgap=1)

        label = wx.StaticText(panel)
        label.SetLabel("选择模型：")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.SelectTrainModelPath = wx.FilePickerCtrl(panel, wildcard=TrainModelWildcard, size=(320, 27))
        self.SelectTrainModelPath.GetPickerCtrl().SetLabel('浏览')
        gridSizer1.Add(self.SelectTrainModelPath, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        label = wx.StaticText(panel)
        label.SetLabel("")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        label = wx.StaticText(panel)
        label.SetLabel("训练数据存储路径：")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.OnlineDataPath = wx.DirPickerCtrl(panel, size=(320, 27))
        self.OnlineDataPath.GetPickerCtrl().SetLabel('浏览')
        gridSizer1.Add(self.OnlineDataPath, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.OnlineStartBtn = wx.Button(panel, label="开始康复训练", size=wx.Size(100, 27))
        self.OnlineStartBtn.Bind(wx.EVT_BUTTON, self.OnOnlineStart)
        gridSizer1.Add(self.OnlineStartBtn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.sbsizer1.Add(gridSizer1, proportion=0, flag=wx.ALL, border=5)

        self.backBtn = wx.Button(panel, label="返回", size=(100, 27))
        self.backBtn.Bind(wx.EVT_BUTTON, self.OnBack)
        gridSizer = wx.FlexGridSizer(cols=1, vgap=1, hgap=1)
        gridSizer.Add(self.backBtn, 0, wx.ALL, 5)
        gridSizer.Add(self.sbsizer1, 0, wx.ALL, 5)
        panel.SetSizerAndFit(gridSizer)
        panel.Center()
        self.Fit()

    def OnBack(self, event):
        self.Close()  # 关闭窗体

    def OnOnlineStart(self, event):
        firstClassNum = self.CueSettingData['firstClassNum']
        secondClassNum = self.CueSettingData['secondClassNum']
        baseline = self.CueSettingData['baselineDuration']
        waitCue = self.CueSettingData['waitCueDuration']
        dispCue = self.CueSettingData['dispCueDuration']
        customFirstCuePath = self.CueSettingData['customFirstClass']
        customSecondCuePath = self.CueSettingData['customSecondClass']
        auditoryCue = self.CueSettingData['auditoryIsChecked']
        SelectTrainModelPath = self.SelectTrainModelPath.GetPath()
        self.DataPath = self.OnlineDataPath.GetPath()
        self.graz = Graz(self, customFirstCuePath, customSecondCuePath, auditoryCue)
        self.stim = MIStimulator(self.graz,
                                 first_class='OVTK_GDF_Left',
                                 number_of_first_class=firstClassNum,
                                 second_class='OVTK_GDF_Right',
                                 number_of_second_class=secondClassNum,
                                 baseline_duration=baseline,
                                 wait_for_cue_duration=waitCue,
                                 display_cue_duration=dispCue)
                                 #feedback_duration=0
        self.dataServer = OnlinensDataServer(self)
        #self.dataServer = OnlineneDataServer(self)
        msg = "总时长: " + str(self.stim.T) + "秒\n" + "是否开始任务?"
        style = wx.OK | wx.CANCEL | wx.CENTRE
        msgbox = wx.MessageDialog(self, msg, "训练任务开始", style)
        if(msgbox.ShowModal() == wx.ID_OK):
            self.graz.Show()
            self.graz.startStim()
            if self.dataServer:
                self.dataServer.configure()
                if(not self.dataServer.connected):
                    self.dataServer.loadTrainModel(SelectTrainModelPath)
                    self.dataServer.loadSettings(self.mainMenuData)
                    self.dataServer.start()
        else:
            return

    # Online 传入cue设置与主窗体设置数据
    def setValue(self, CueSettingData, mainMenuData):
        self.CueSettingData = CueSettingData
        self.mainMenuData = mainMenuData

    # Online 关闭窗体时返回数据给主窗体
    def getValue(self):
        OnlineTestData = {
            'SelectTrainModelPath': self.SelectTrainModelPath.GetPath(),
            'OnlineDataPath': self.OnlineDataPath.GetPath()
        }
        return OnlineTestData

    # Online 加载初始化数据
    def initData(self, OnlineTestData):
        self.SelectTrainModelPath.SetPath(OnlineTestData['SelectTrainModelPath'])
        self.OnlineDataPath.SetPath(OnlineTestData['OnlineDataPath'])

    def grazFinish(self):
        if self.dataServer:
            self.dataServer.stop()
            print('Saving Signal...')
            path = self.DataPath
            self.dataServer.saveData(path)
            print('Signal Saved')

