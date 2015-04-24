#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys

import wx

class GuiEvent(wx.PyCommandEvent):
    def __init__(self, evt_type, id):
        wx.PyCommandEvent.__init__(self, evt_type, id)
        self.args = None

    def get_args(self):
        return self.args

    def set_args(self, args):
        self.args = args
