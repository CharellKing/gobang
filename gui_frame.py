#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys

import wx

from gui_panel import GuiPanel

class GuiFrame(wx.Frame):
    def __init__(self, cmd_controller, title = "gobang"):
        wx.Frame.__init__(self,
                          None,
                          title = title,
                          size=(620,600),
                          style = wx.CLOSE_BOX | wx.CAPTION | wx.SYSTEM_MENU | wx.MINIMIZE_BOX)
        vbox = wx.BoxSizer(wx.VERTICAL)
        #frame上有panel,panel才能添加button，编辑框等等
        self.panel = GuiPanel(self, cmd_controller)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        vbox.Add(self.panel, 1, wx.EXPAND | wx.ALL, 5)
        self.Center()

    #处理关闭消息
    def OnClose(self, evt):
        if True == self.panel.cmd_controller.is_starting():
            dlg = wx.MessageDialog(None, "您正处于游戏中, 是否要离开", '提示', wx.YES_NO | wx.ICON_INFORMATION)
            if dlg.ShowModal() == wx.ID_YES:
                self.panel.Close()
                self.Destroy()
            dlg.Destroy()
