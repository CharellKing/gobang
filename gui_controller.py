#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys
import gettext
import wx

from cmd_controller import CmdController
from gui_app import GuiApp
from gui_login_dialog import NicknameDlg

class GuiController(object):
    def __init__(self):
        self.cmd_controller = CmdController()

    def run(self):

        gettext.install("nickname") # replace with the appropriate catalog name
        app = wx.PySimpleApp(0)
        wx.InitAllImageHandlers()
        nickname_dlg = NicknameDlg(None, wx.ID_ANY, "")
        app.SetTopWindow(nickname_dlg)
        nickname_dlg.Show()
        app.MainLoop()
        app.Destroy()

        if None == NicknameDlg.nickname or "" == NicknameDlg.nickname:
            return
        NicknameDlg.nickname = 'ck'
        self.cmd_controller.set_nickname(NicknameDlg.nickname)
        app = GuiApp(self.cmd_controller, 0)
        app.MainLoop()
