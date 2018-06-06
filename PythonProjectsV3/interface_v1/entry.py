import wx
import wx.adv as wxadv

#rom .Graz import *
#from .nsDataServer import *
from InitWindow import MainWindow

app = wx.App()
win = MainWindow()
win.Show()
print('Ready')
app.MainLoop()
