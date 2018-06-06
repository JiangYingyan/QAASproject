import wx


class settingCueWindow(wx.Dialog):
    def __init__(self, parent, title):
        super(settingCueWindow, self).__init__(parent, title=title, size=(525, 360))
        self.Centre()
        panel = wx.Panel(self)

        gridSizer1 = wx.FlexGridSizer(cols=4, vgap=10, hgap=1)
        imgWildcard = "Image File (.gif, .bmp, .jpg, .png)" + "|*.gif;*.bmp;*.jpg;*.png"

        self.firstClassNumCtrl = wx.SpinCtrl(panel, value='10', min=0, max=50)
        label = wx.StaticText(panel)
        label.SetLabel("运动想象次数：")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer1.Add(self.firstClassNumCtrl, 0, wx.ALL, 5)

        self.secondClassNumCtrl = wx.SpinCtrl(panel, value='10', min=0, max=50)
        label = wx.StaticText(panel)
        label.SetLabel("放松模式次数：")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer1.Add(self.secondClassNumCtrl, 0, wx.ALL, 5)

        self.baselineCtrl = wx.SpinCtrl(panel, value='5', min=0, max=20)
        label = wx.StaticText(panel)
        label.SetLabel("准备时长（秒）：")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer1.Add(self.baselineCtrl, 0, wx.ALL, 5)

        self.waitCueCtrl = wx.SpinCtrl(panel, value='2', min=0, max=10)
        label = wx.StaticText(panel)
        label.SetLabel("提示间隔（秒）：")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer1.Add(self.waitCueCtrl, 0, wx.ALL, 5)

        self.dispCueCtrl = wx.SpinCtrl(panel, value='5', min=0, max=20)
        label = wx.StaticText(panel)
        label.SetLabel("提示时长（秒）：")
        gridSizer1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridSizer1.Add(self.dispCueCtrl, 0, wx.ALL, 5)

        gridSizer2 = wx.FlexGridSizer(cols=2, vgap=10, hgap=1)

        label = wx.StaticText(panel)
        label.SetLabel("运动想象提示图：")
        gridSizer2.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.customFirstClassCtrl = wx.FilePickerCtrl(panel, wildcard=imgWildcard, size=(385, 27))
        self.customFirstClassCtrl.GetPickerCtrl().SetLabel('浏览')
        gridSizer2.Add(self.customFirstClassCtrl, 0, wx.ALL, 5)

        label = wx.StaticText(panel)
        label.SetLabel("放松模式提示图：")
        gridSizer2.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.customSecondClassCtrl = wx.FilePickerCtrl(panel, wildcard=imgWildcard, size=(385, 27))
        self.customSecondClassCtrl.GetPickerCtrl().SetLabel('浏览')
        gridSizer2.Add(self.customSecondClassCtrl, 0, wx.ALL, 5)

        # auditory cue 听觉提示复选框
        self.auditoryCue= wx.CheckBox(panel, -1, "听觉提示")
        gridSizer2.Add(self.auditoryCue, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        # self.auditoryCue.Disable()  #TODO: Remove this line when function implemented

        self.submitBtn = wx.Button(panel, label="提交", size=(100, 27))
        self.submitBtn.Bind(wx.EVT_BUTTON, self.OnSubmit)
        gridSizer2.Add(self.submitBtn, 0, wx.ALL, 5)

        gridSizer = wx.FlexGridSizer(cols=1, vgap=1, hgap=1)
        gridSizer.Add(gridSizer1, 0, wx.ALL, 5)
        gridSizer.Add(gridSizer2, 0, wx.ALL, 5)
        panel.SetSizerAndFit(gridSizer)
        panel.Center()
        self.Fit()

    def OnSubmit(self, event):
        self.Close()  # 关闭窗体

    def getValue(self):
        cueSettingData = {
            'firstClassNum': self.firstClassNumCtrl.GetValue(),
            'secondClassNum': self.secondClassNumCtrl.GetValue(),
            'baselineDuration': self.baselineCtrl.GetValue(),
            'waitCueDuration': self.waitCueCtrl.GetValue(),
            'dispCueDuration': self.dispCueCtrl.GetValue(),
            'customFirstClass': self.customFirstClassCtrl.GetPath(),
            'customSecondClass': self.customSecondClassCtrl.GetPath(),
            'auditoryIsChecked': self.auditoryCue.IsChecked()
        }
        return cueSettingData

    def initData(self, CueSettingData):
        self.firstClassNumCtrl.SetValue(CueSettingData['firstClassNum'])
        self.secondClassNumCtrl.SetValue(CueSettingData['secondClassNum'])
        self.baselineCtrl.SetValue(CueSettingData['baselineDuration'])
        self.waitCueCtrl.SetValue(CueSettingData['waitCueDuration'])
        self.dispCueCtrl.SetValue(CueSettingData['dispCueDuration'])
        self.customFirstClassCtrl.SetPath(CueSettingData['customFirstClass'])
        self.customSecondClassCtrl.SetPath(CueSettingData['customSecondClass'])
        self.auditoryCue.SetValue(CueSettingData['auditoryIsChecked'])


