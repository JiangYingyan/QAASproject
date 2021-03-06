# -*- coding: utf-8 -*-
import wx

from Graz import Graz, MIStimulator
from nsDataServer import nsDataServer
from OnlinensDataServer import OnlinensDataServer
import pickle

from settingWindow import settingCueWindow
from acqOrOnlineWindow import acqAndTrainModelWindow, OnlineTestWindow

# 初始化配置窗体
class MainWindow(wx.Frame):
    def __init__(self):
        super(MainWindow, self).__init__(None, title="主界面", size=(400, 400))
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE & ~(
            wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.initUI()
        self.OnReset(None)
        self.Fit()
        self.Centre()

        # Bind: 响应button事件
        self.settingCueBtn.Bind(wx.EVT_BUTTON, self.OnCueSetting)
        self.dataServer = None

    def initUI(self):
        self.DestroyChildren()
        # wx.Panel: 窗口的容器
        panel = wx.Panel(self)

        # wx.FlexGridSizer: 二维网状布局(rows, cols, vgap, hgap)=>(行数, 列数, 垂直方向行间距, 水平方向列间距)
        sessionType = ['校准任务', '训练任务']
        # 初始化各个窗体的值
        self.CueSettingData = {
            'firstClassNum': 10,
            'secondClassNum': 10,
            'baselineDuration': 10,
            'waitCueDuration': 2,
            'dispCueDuration': 8,
            'customFirstClass': '..\\CueMaterial\\lefthand.gif',  # 运动
            'customSecondClass': '..\\CueMaterial\\restimg.png',  # 放松
            'auditoryIsChecked': True
        }
        self.mainMenuData = {
            'visualFeedback': True,
            'exoskeletonFeedback': True,
            'comNum': 17,  # 端口号
            'controlStrategyTrial': False,
            'controlStrategyEpoch': True,  # Trial和Epoch仅能有1个True
            'angleStart': 0,  # 初始角度
            'angleRange': 60,  # 角度范围 最大79°
            'velocity': 30
        }
        self.acqAndTrainModelData = {
            'accquDataPath': '',
            'TrainDataPath': '',
            'TrainModelPath': ''
        }
        self.OnlineTestData = {
            'SelectTrainModelPath': '',
            'OnlineDataPath': ''
        }

        gridSizer1 = wx.FlexGridSizer(cols=6, vgap=10, hgap=1)
        label = wx.StaticText(panel)
        label.SetLabel("运动想象")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.firstClassNumLabel = wx.StaticText(panel)
        self.firstClassNumLabel.SetLabel("10")
        gridSizer1.Add(self.firstClassNumLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        label = wx.StaticText(panel)
        label.SetLabel("个； 放松状态")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.secondClassNumLabel = wx.StaticText(panel)
        self.secondClassNumLabel.SetLabel("10")
        gridSizer1.Add(self.secondClassNumLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        label = wx.StaticText(panel)
        label.SetLabel("个")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.settingCueBtn = wx.Button(panel, label="设置提示界面")
        gridSizer1.Add(self.settingCueBtn, 0, wx.ALL, 5)

        gridSizer2 = wx.FlexGridSizer(cols=4, vgap=10, hgap=1)

        self.visualFeedback = wx.CheckBox(panel, -1, "视觉反馈")
        gridSizer2.Add(self.visualFeedback, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.exoskeletonFeedback = wx.CheckBox(panel, -1, "外骨骼反馈")
        gridSizer2.Add(self.exoskeletonFeedback, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.comNum = wx.SpinCtrl(panel, value='17', min=0, max=10000, size=(70, 27))
        label = wx.StaticText(panel)
        label.SetLabel("| 端口号：")
        gridSizer2.Add(label, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        gridSizer2.Add(self.comNum, 0, wx.ALL, 5)

        # exoskeleton box 外骨骼
        sbox3 = wx.StaticBox(panel, -1, label=u'外骨骼设置')
        self.sbsizer3 = wx.StaticBoxSizer(sbox3, wx.VERTICAL)
        gridSizer3 = wx.FlexGridSizer(cols=3, vgap=10, hgap=1)

        label = wx.StaticText(panel)
        label.SetLabel("外骨骼控制策略：")
        gridSizer3.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.controlStrategyTrial = wx.RadioButton(panel, label='分段反馈')
        self.controlStrategyEpoch = wx.RadioButton(panel, label='实时反馈')
        self.controlStrategyEpoch.SetValue(True)
        gridSizer3.Add(self.controlStrategyTrial, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer3.Add(self.controlStrategyEpoch, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        label = wx.StaticText(panel)
        label.SetLabel("初始角度：")
        gridSizer3.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.angleStart = wx.SpinCtrl(panel, value='0', min=0, max=79, size=(100, 27))  # 外骨骼初始角度
        gridSizer3.Add(self.angleStart, 0, wx.ALL, 5)
        label = wx.StaticText(panel)
        label.SetLabel("")
        gridSizer3.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        label = wx.StaticText(panel)
        label.SetLabel("角度范围：")
        gridSizer3.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.angleRange = wx.SpinCtrl(panel, value='60', min=0, max=79, size=(100, 27))  # 外骨骼角度范围
        gridSizer3.Add(self.angleRange, 0, wx.ALL, 5)
        label = wx.StaticText(panel)
        label.SetLabel("(最大：79°-初始)")
        gridSizer3.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.velocity = wx.SpinCtrl(panel, value='30', min=10, max=80, size=(100, 27))  # 外骨骼速度
        label = wx.StaticText(panel)
        label.SetLabel("速度：")
        gridSizer3.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer3.Add(self.velocity, 0, wx.ALL, 5)
        self.sbsizer3.Add(gridSizer3, proportion=0, flag=wx.ALL, border=5)


        gridSizer4 = wx.FlexGridSizer(cols=3, vgap=10, hgap=1)
        label = wx.StaticText(panel)
        label.SetLabel("任务类型：")
        gridSizer4.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.sessionTypeCtrl = wx.Choice(panel, name="Session Type", choices=sessionType)
        self.sessionTypeCtrl.SetSelection(0)
        gridSizer4.Add(self.sessionTypeCtrl, 0, wx.ALL, 5)

        self.nextBtn = wx.Button(panel, label="下一步", size=(100, 27))
        self.nextBtn.Bind(wx.EVT_BUTTON, self.OnNext)
        gridSizer4.Add(self.nextBtn, 0, wx.ALL, 5)

        self.statusBar = self.CreateStatusBar()  # 状态栏
        self.statusBar.SetStatusText(u'……')

        gridSizer = wx.FlexGridSizer(cols=1, vgap=1, hgap=1)
        gridSizer.Add(gridSizer1, 0, wx.ALL, 5)
        gridSizer.Add(gridSizer2, 0, wx.ALL, 5)
        gridSizer.Add(self.sbsizer3, 0, wx.ALL, 5)
        gridSizer.Add(gridSizer4, 0, wx.ALL, 5)

        panel.SetSizerAndFit(gridSizer)
        panel.Center()
        self.initData(self.mainMenuData)
        self.Fit()

    def initData(self, mainMenuData):
        self.visualFeedback.SetValue(mainMenuData['visualFeedback'])
        self.exoskeletonFeedback.SetValue(mainMenuData['exoskeletonFeedback'])
        self.comNum.SetValue(mainMenuData['comNum'])
        self.controlStrategyTrial.SetValue(mainMenuData['controlStrategyTrial'])
        self.controlStrategyEpoch.SetValue(mainMenuData['controlStrategyEpoch'])
        self.angleStart.SetValue(mainMenuData['angleStart'])
        self.angleRange.SetValue(mainMenuData['angleRange'])
        self.velocity.SetValue(mainMenuData['velocity'])

    def OnCueSetting(self, event):
        settingWindow = settingCueWindow(self, "提示界面设置")
        settingWindow.initData(self.CueSettingData)
        settingWindow.ShowModal()
        self.CueSettingData = settingWindow.getValue()
        self.firstClassNumLabel.SetLabel(str(self.CueSettingData['firstClassNum']))
        self.secondClassNumLabel.SetLabel(str(self.CueSettingData['secondClassNum']))

    def OnNext(self, event):
        self.mainMenuData = {
            'visualFeedback': self.visualFeedback.GetValue(),  # 视觉反馈
            'exoskeletonFeedback': self.exoskeletonFeedback.GetValue(),  # 外骨骼反馈
            'comNum': self.comNum.GetValue(),  # 端口号
            'controlStrategyTrial': self.controlStrategyTrial.GetValue(),  # 按trial反馈
            'controlStrategyEpoch': self.controlStrategyEpoch.GetValue(),  # 按epoch反馈
            'angleStart': self.angleStart.GetValue(),
            'angleRange': self.angleRange.GetValue(),
            'velocity': self.velocity.GetValue()
        }
        sessionTypeIdx = self.sessionTypeCtrl.GetCurrentSelection()
        sessionType = self.sessionTypeCtrl.GetString(sessionTypeIdx)
        if sessionType == '校准任务':
            accAndTrainModel = acqAndTrainModelWindow(self, "校准任务")
            accAndTrainModel.initData(self.acqAndTrainModelData)
            accAndTrainModel.setValue(self.CueSettingData, self.mainMenuData)
            accAndTrainModel.ShowModal()
            self.acqAndTrainModelData = accAndTrainModel.getValue()
        elif sessionType == '训练任务':
            OnlineTest = OnlineTestWindow(self, "训练任务")
            OnlineTest.initData(self.OnlineTestData)
            OnlineTest.setValue(self.CueSettingData, self.mainMenuData)
            OnlineTest.ShowModal()
            self.OnlineTestData = OnlineTest.getValue()

    def OnReset(self, event):
        self.initUI()

    def setDataServer(self, dataServer=None):
        self.dataServer = dataServer


