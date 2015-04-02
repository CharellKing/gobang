#!/usr/bin/python

# coding=utf-8

import os
import sys
import wx

import math
import random

from gobang_frame import GobangFrame

cur_dir = os.path.split(os.path.realpath(__file__))[0]

class Main(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        gobang_frame = GobangFrame()
        self.SetTopWindow(gobang_frame)
        gobang_frame.Show()


if __name__ == "__main__":
    app = Main(0)
    app.MainLoop()
