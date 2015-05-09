#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys

import wx
from gui_frame import GuiFrame

class GuiApp(wx.App):
    def __init__(self, cmd_controller, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        gui_frame = GuiFrame(cmd_controller, "%s@gobang" %(cmd_controller.nickname))
        self.SetTopWindow(gui_frame)
        gui_frame.Show()
