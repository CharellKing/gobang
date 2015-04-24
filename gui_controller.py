#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys

from cmd_controller import CmdController
from gui_app import GuiApp

class GuiController(object):
    def __init__(self):
        self.cmd_controller = CmdController()

    def run(self):
        self.cmd_controller.set_nickname("ck")
        app = GuiApp(self.cmd_controller, 0)
        app.MainLoop()
