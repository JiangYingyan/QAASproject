# -*- coding: utf-8 -*-
import wx

from Graz import Graz, MIStimulator
from nsDataServer import nsDataServer
from OnlinensDataServer import OnlinensDataServer
import pickle

# 初始化配置窗体
class MainWindow(wx.Frame):
    def __init__(self):
        super(MainWindow, self).__init__(None, title="Main", size=(900, 960))
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE & ~(
            wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.initUI()
        self.OnReset(None)
        self.Fit()
        self.Centre()

        # Bind: 响应button事件
        # self.resetBtn.Bind(wx.EVT_BUTTON, self.OnReset)
        self.AccStartBtn.Bind(wx.EVT_BUTTON, self.OnAccStart)
        self.TrainModelBtn.Bind(wx.EVT_BUTTON, self.OnTrainModel)
        self.OnlineStartBtn.Bind(wx.EVT_BUTTON, self.OnOnlineStart)
        self.dataServer = None

    def initUI(self):
        self.DestroyChildren()
        # wx.Panel: 窗口的容器
        panel = wx.Panel(self)

        # wx.FlexGridSizer: 二维网状布局(rows, cols, vgap, hgap)=>(行数, 列数, 垂直方向行间距, 水平方向列间距)
        gridSizer1 = wx.FlexGridSizer(cols=4, vgap=10, hgap=1)
        stimSet = ['OVTK_GDF_Left', 'OVTK_GDF_Right',
                   'OVTK_GDF_Down', 'OVTK_GDF_Up']
        imgWildcard = "Image File (.gif, .bmp, .jpg, .png)" + "|*.gif;*.bmp;*.jpg;*.png"
        dataWildcard = "npz Data File (.npz)" + "|*.npz"
        TrainModelWildcard = "pkl Data File (.pkl)" + "|*.pkl"

        # wx.Choice: 下拉框
        # self.firstClassCtrl = wx.Choice(panel, name="First Class", choices=stimSet)
        # self.firstClassCtrl.SetSelection(0)
        # label = wx.StaticText(panel)
        # label.SetLabel("First Class Stimulation")
        # gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        # gridSizer1.Add(self.firstClassCtrl, 0, wx.ALL, 5)
        #
        # self.secondClassCtrl = wx.Choice(panel, name="Second Class", choices=stimSet)
        # self.secondClassCtrl.SetSelection(1)
        # label = wx.StaticText(panel)
        # label.SetLabel("Second Class Stimulation")
        # gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        # gridSizer1.Add(self.secondClassCtrl, 0, wx.ALL, 5)

        # wx.SpinCtrl: 可用上下键改变数字值的文本控件
        self.firstClassNumCtrl = wx.SpinCtrl(panel, value='10', min=0, max=20)
        label = wx.StaticText(panel)
        label.SetLabel("First Class Stimulation Number")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer1.Add(self.firstClassNumCtrl, 0, wx.ALL, 5)

        self.secondClassNumCtrl = wx.SpinCtrl(panel, value='10', min=0, max=20)
        label = wx.StaticText(panel)
        label.SetLabel("Second Class Stimulation Number")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer1.Add(self.secondClassNumCtrl, 0, wx.ALL, 5)

        # wx.FilePickerCtrl: 文件目录选择
        # 自定义提示图片
        self.customFirstClassCtrl = wx.FilePickerCtrl(panel, wildcard=imgWildcard)
        label = wx.StaticText(panel)
        label.SetLabel("First Class Custom Cue")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer1.Add(self.customFirstClassCtrl, 0, wx.ALL, 5)

        self.customSecondClassCtrl = wx.FilePickerCtrl(
            panel, wildcard=imgWildcard)
        label = wx.StaticText(panel)
        label.SetLabel("Second Class Custom Cue")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer1.Add(self.customSecondClassCtrl, 0, wx.ALL, 5)

        sbox1 = wx.StaticBox(panel, -1, label=u'Class Select')
        self.sbsizer1 = wx.StaticBoxSizer(sbox1, wx.VERTICAL)
        self.sbsizer1.Add(gridSizer1, proportion=0, flag=wx.EXPAND, border=5)

        gridSizer2 = wx.FlexGridSizer(cols=5, vgap=10, hgap=1)

        self.baselineCtrl = wx.SpinCtrl(panel, value='5', min=0, max=20)
        label = wx.StaticText(panel)
        label.SetLabel("Baseline Duration (sec)")
        gridSizer2.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer2.Add(self.baselineCtrl, 0, wx.ALL, 5)

        self.waitCueCtrl = wx.SpinCtrl(panel, value='1', min=0, max=10)
        label = wx.StaticText(panel)
        label.SetLabel("Waiting For Cue Duration (sec)")
        gridSizer2.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer2.Add(self.waitCueCtrl, 0, wx.ALL, 5)

        # auditory cue 听觉提示复选框
        self.auditoryCue = wx.CheckBox(panel, -1, "Auditory cue")
        gridSizer2.Add(self.auditoryCue, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.auditoryCue.Disable()  #TODO: Remove this line when function implemented

        self.dispCueCtrl = wx.SpinCtrl(panel, value='5', min=0, max=20)
        label = wx.StaticText(panel)
        label.SetLabel("Display Cue Duration (sec)")
        gridSizer2.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer2.Add(self.dispCueCtrl, 0, wx.ALL, 5)

        self.feedbackCtrl = wx.SpinCtrl(panel, value='1', min=0, max=20)
        label = wx.StaticText(panel)
        label.SetLabel("Feedback Duration (sec)")
        gridSizer2.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer2.Add(self.feedbackCtrl, 0, wx.ALL, 5)

        # Accquisition Session box
        sbox2 = wx.StaticBox(panel, -1, label=u'Accquisition Session')
        self.sbsizer2 = wx.StaticBoxSizer(sbox2, wx.VERTICAL)
        gridSizer3 = wx.FlexGridSizer(cols=3, vgap=10, hgap=1)

        self.accquDataPath = wx.DirPickerCtrl(panel, size=(470, 25))
        label = wx.StaticText(panel)
        label.SetLabel("Accquisition Data Save Path")
        gridSizer3.Add(label,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer3.Add(self.accquDataPath,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.AccStartBtn = wx.Button(panel, label="Start Accquisition", size=wx.Size(150, 36))
        gridSizer3.Add(self.AccStartBtn,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.sbsizer2.Add(gridSizer3, proportion=0, flag=wx.ALL, border=5)

        # Train Model box
        sbox3 = wx.StaticBox(panel, -1, label=u'Train Model')
        self.sbsizer3 = wx.StaticBoxSizer(sbox3, wx.VERTICAL)
        gridSizer4 = wx.FlexGridSizer(cols=3, vgap=10, hgap=1)

        self.TrainDataPath = wx.FilePickerCtrl(panel, wildcard=dataWildcard, size=(500, 25))
        label = wx.StaticText(panel)
        label.SetLabel("Select Train Data")
        gridSizer4.Add(label,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer4.Add(self.TrainDataPath,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        label = wx.StaticText(panel)
        label.SetLabel("")
        gridSizer4.Add(label,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.TrainModelPath = wx.DirPickerCtrl(panel, size=(500, 25))
        label = wx.StaticText(panel)
        label.SetLabel("Train Model Save Path")
        gridSizer4.Add(label,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer4.Add(self.TrainModelPath,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.TrainModelBtn = wx.Button(panel, label="Start Train Model", size=wx.Size(150, 36))
        gridSizer4.Add(self.TrainModelBtn,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.sbsizer3.Add(gridSizer4, proportion=0, flag=wx.ALL, border=5)

        # Online Test box
        sbox4 = wx.StaticBox(panel, -1, label=u'Online Test')
        self.sbsizer4 = wx.StaticBoxSizer(sbox4, wx.VERTICAL)
        gridSizer5 = wx.FlexGridSizer(cols=3, vgap=10, hgap=1)

        self.SelectTrainModelPath = wx.FilePickerCtrl(panel, wildcard=TrainModelWildcard, size=(505, 25))
        label = wx.StaticText(panel)
        label.SetLabel("Select Train Model")
        gridSizer5.Add(label,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer5.Add(self.SelectTrainModelPath,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        label = wx.StaticText(panel)
        label.SetLabel("")
        gridSizer5.Add(label,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.OnlineDataPath = wx.DirPickerCtrl(panel, size=(505, 25))
        label = wx.StaticText(panel)
        label.SetLabel("Online Data Save Path")
        gridSizer5.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer5.Add(self.OnlineDataPath, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.OnlineStartBtn = wx.Button(panel, label="Start Online Test", size=wx.Size(150, 36))
        gridSizer5.Add(self.OnlineStartBtn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.sbsizer4.Add(gridSizer5, proportion=0, flag=wx.ALL, border=5)


        # exoskeleton box
        sbox5 = wx.StaticBox(panel, -1, label=u'Exoskeleton Settings')
        self.sbsizer5 = wx.StaticBoxSizer(sbox5, wx.VERTICAL)
        gridSizer6 = wx.FlexGridSizer(cols=7, vgap=10, hgap=1)

        label = wx.StaticText(panel)
        label.SetLabel("Exoskeleton control strategy")
        gridSizer6.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.controlStrategyTrial = wx.RadioButton(panel, label='TrialBased')
        self.controlStrategyEpoch = wx.RadioButton(panel, label='EpochBased')
        gridSizer6.Add(self.controlStrategyTrial, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer6.Add(self.controlStrategyEpoch, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)


        self.angleRange = wx.SpinCtrl(panel, value='90', min=0, max=160)  # 外骨骼角度范围
        label = wx.StaticText(panel)
        label.SetLabel("  angle range")
        gridSizer6.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer6.Add(self.angleRange, 0, wx.ALL, 5)

        self.velocity = wx.SpinCtrl(panel, value='10', min=0, max=20)  # 外骨骼速度
        label = wx.StaticText(panel)
        label.SetLabel(" Velocity")
        gridSizer6.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer6.Add(self.velocity, 0, wx.ALL, 5)

        self.sbsizer5.Add(gridSizer6, proportion=0, flag=wx.ALL, border=5)


        self.statusBar = self.CreateStatusBar()  # 状态栏
        self.statusBar.SetStatusText(u'……')

        gridSizer = wx.FlexGridSizer(cols=1, vgap=1, hgap=1)
        gridSizer.Add(self.sbsizer1, 0, wx.ALL, 5)
        gridSizer.Add(gridSizer2, 0, wx.ALL, 5)
        gridSizer.Add(self.sbsizer2, 0, wx.ALL, 5)
        gridSizer.Add(self.sbsizer3, 0, wx.ALL, 5)
        gridSizer.Add(self.sbsizer4, 0, wx.ALL, 5)
        gridSizer.Add(self.sbsizer5, 0, wx.ALL, 5)

        panel.SetSizerAndFit(gridSizer)
        panel.Center()

        self.Fit()

    def OnAccStart(self, event):
        # firstClassIdx = self.firstClassCtrl.GetCurrentSelection()
        # firstClass = self.firstClassCtrl.GetString(firstClassIdx)
        firstClassNum = self.firstClassNumCtrl.GetValue()
        # secondClassIdx = self.secondClassCtrl.GetCurrentSelection()
        # secondClass = self.secondClassCtrl.GetString(secondClassIdx)
        secondClassNum = self.secondClassNumCtrl.GetValue()
        baseline = self.baselineCtrl.GetValue()
        waitCue = self.waitCueCtrl.GetValue()
        dispCue = self.dispCueCtrl.GetValue()
        feedback = self.feedbackCtrl.GetValue()
        self.DataPath = self.accquDataPath.GetPath()
        customFirstCuePath = self.customFirstClassCtrl.GetPath()
        customSecondCuePath = self.customSecondClassCtrl.GetPath()
        auditoryCue = self.auditoryCue.IsChecked()
        self.graz = Graz(self, customFirstCuePath, customSecondCuePath, auditoryCue)
        self.stim = MIStimulator(self.graz,
                                 first_class='OVTK_GDF_Left',
                                 number_of_first_class=firstClassNum,
                                 second_class='OVTK_GDF_Right',
                                 number_of_second_class=secondClassNum,
                                 baseline_duration=baseline,
                                 wait_for_cue_duration=waitCue,
                                 display_cue_duration=dispCue,
                                 feedback_duration=feedback)
        self.dataServer = nsDataServer(self)
        msg = "Graz Stimulator is Ready!\n" + "Total Time of the Session is: " + \
            str(self.stim.T)+"s\n"+"Start Now?"
        style = wx.OK | wx.CANCEL | wx.CENTRE
        msgbox = wx.MessageDialog(self, msg, "Experiment is Ready", style)
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
        pickle.dump(classifier_model, f1)
        pickle.dump(csp_ProjMatrix, f1)
        f1.close()
        self.statusBar.SetStatusText('Train Model Finished.')

    def OnOnlineStart(self, event):
        # firstClass = self.firstClassCtrl.GetCurrentSelection()
        # firstClass = self.firstClassCtrl.GetString(firstClass)
        firstClassNum = self.firstClassNumCtrl.GetValue()
        # secondClass = self.secondClassCtrl.GetCurrentSelection()
        # secondClass = self.secondClassCtrl.GetString(secondClass)
        secondClassNum = self.secondClassNumCtrl.GetValue()
        baseline = self.baselineCtrl.GetValue()
        waitCue = self.waitCueCtrl.GetValue()
        dispCue = self.dispCueCtrl.GetValue()
        feedback = self.feedbackCtrl.GetValue()
        self.DataPath = self.OnlineDataPath.GetPath()
        SelectTrainModelPath = self.SelectTrainModelPath.GetPath()
        self.graz = Graz(self)
        self.stim = MIStimulator(self.graz,
                                 first_class='OVTK_GDF_Left',
                                 number_of_first_class=firstClassNum,
                                 second_class='OVTK_GDF_Right',
                                 number_of_second_class=secondClassNum,
                                 baseline_duration=baseline,
                                 wait_for_cue_duration=waitCue,
                                 display_cue_duration=dispCue,
                                 feedback_duration=feedback)
        self.dataServer = OnlinensDataServer(self)
        msg = "Graz Stimulator is Ready!\n" + \
            "Total Time of the Session is: " + \
            str(self.stim.T)+"s\n"+"Start Now?"
        style = wx.OK | wx.CANCEL | wx.CENTRE
        msgbox = wx.MessageDialog(self, msg, "Experiment is Ready", style)
        if(msgbox.ShowModal() == wx.ID_OK):
            self.graz.Show()
            self.graz.startStim()
            if self.dataServer:
                self.dataServer.configure()
                if(not self.dataServer.connected):
                    self.dataServer.loadTrainModel(SelectTrainModelPath)
                    self.dataServer.start()
        else:
            return

    def OnReset(self, event):
        self.initUI()

    def setDataServer(self, dataServer=None):
        self.dataServer = dataServer

    def grazFinish(self):
        if self.dataServer:
            self.dataServer.stop()
            print('Saving Signal...')
            path = self.DataPath
            self.dataServer.saveData(path)
            print('Signal Saved')
            print('File Path:'+path)
