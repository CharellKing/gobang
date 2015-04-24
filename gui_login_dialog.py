#!/usr/bin/python
#-*-coding:utf-8-*-


import wx

import gettext


class NicknameDlg(wx.Dialog):
    nickname = None
    def __init__(self, *args, **kwds):
        # begin wxGlade: LoginDlg.__init__
        kwds["style"] = wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.static_text = wx.StaticText(self, wx.ID_ANY, _(u"请输入你的昵称:"))
        self.nick_text = wx.TextCtrl(self, wx.ID_ANY, "")
        self.ok_btn = wx.Button(self, wx.ID_ANY, _(u"确定"))
        self.cancel_btn = wx.Button(self, wx.ID_ANY, _(u"取消"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnOk, self.ok_btn)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancel_btn)


        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: LoginDlg.__set_properties
        self.SetTitle(_(u"昵称"))
        # end wxGlade

    def OnOk(self, evt):
        NicknameDlg.nickname = self.nick_text.GetValue()
        self.Destroy()

    def OnCancel(self, evt):
        NicknameDlg.nickname = None
        self.Destroy()


    def __do_layout(self):
        # begin wxGlade: NicknameDlg.__do_layout
        grid_sizer_1 = wx.GridSizer(2, 2, 0, 0)
        grid_sizer_1.Add(self.static_text, 0, 0, 0)
        grid_sizer_1.Add(self.nick_text, 0, 0, 0)
        grid_sizer_1.Add(self.ok_btn, 0, 0, 0)
        grid_sizer_1.Add(self.cancel_btn, 0, 0, 0)
        self.SetSizer(grid_sizer_1)
        grid_sizer_1.Fit(self)
        self.Layout()
        # end wxGlade
