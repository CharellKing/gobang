#!/usr/bin/python

import wx

from gobang_panel import GobangPanel

class GobangFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,
                          None,
                          title = "gobang",
                          size=(620,500),
                          style = wx.CLOSE_BOX | wx.CAPTION | wx.SYSTEM_MENU | wx.MINIMIZE_BOX)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.panel = GobangPanel(self)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        vbox.Add(self.panel, 1, wx.EXPAND | wx.ALL, 5)
        self.Center()

    def OnClose(self, evt):
        self.panel.Destroy()
        self.Destroy()
