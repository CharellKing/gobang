#!/usr/bin/python

import wx

class MyEvent(wx.PyCommandEvent):
    EVT_TURN_OTHER_TYPE = wx.NewEventType()
    EVT_TURN_OTHER = wx.PyEventBinder(EVT_TURN_OTHER_TYPE, 1)
    EVT_TURN_ME_TYPE = wx.NewEventType()
    EVT_TURN_ME = wx.PyEventBinder(EVT_TURN_ME_TYPE, 1)

    def __init__(self, evt_type, id):
        wx.PyCommandEvent.__init__(self, evt_type, id)
        self.args = None

    def get_args(self):
        return self.args

    def set_args(self, args):
        self.args = args
