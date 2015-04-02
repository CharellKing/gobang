#!/usr/bin/python

import sys, os, wx
import wx.lib.newevent
import time

from gobang_stone import Stone, Gobang
from  gobang_network import GobangServer, GobangClient
from my_event import MyEvent

cur_dir = os.path.split(os.path.realpath(__file__))[0]

class GobangPanel(wx.Panel):
    FACTOR = 24.0
    GRID_SIZE = 24
    TIME_OUT = 5
    TOTAL_LINE_GRID = 15

    ROBOT_OPT = True
    NETWORK_OPT = False

    def __init__(self, parent):
        self.frame = parent
        self.who_do = None
        self.my_color = None
        self.count = GobangPanel.TIME_OUT

        self.digit_bmps = None
        self.robot_radio = None
        self.network_radio = None
        self.ip_static_text = None
        self.ip_addr = None
        self.port_static_text = None
        self.port = None
        self.listen_btn = None
        self.connect_btn = None
        self.start_btn = None
        self.stop_btn = None
        self.status_static = None

        self.network = None

        self.robot_or_network = GobangPanel.ROBOT_OPT
        self.oper = {}
        self.is_start = False

        self.gobang = Gobang()

        self.InitCtrl(parent)
        self.InitEvent()

    def InitCtrl(self, parent):
        wx.Panel.__init__(self, parent=parent)

        self.robot_radio = wx.RadioButton( self, wx.ID_ANY, "robot", (390, 100), (80, 30), 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRobotRadio, self.robot_radio)

        self.network_radio = wx.RadioButton( self, wx.ID_ANY, "network", (530, 100), (80, 30), 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnNetWorkRadio, self.network_radio)

        self.ip_static_text = wx.StaticText(self, -1, "ip:", pos = (390, 150), size = (15, 30), style = wx.ALL)
        self.ip_addr = wx.TextCtrl(self, -1, "127.0.0.1", (420, 150), (80, 30), style = wx.ALL)

        self.port_static_text = wx.StaticText(self, -1, "port:", pos = (510, 150), size = (30, 30), style = wx.ALL)
        self.port = wx.TextCtrl(self, -1, "8888", (550, 150), (50, 30), style = wx.ALL)

        self.listen_btn = wx.Button( self, wx.ID_ANY, "Listen", (390, 200), (100, 30), 0)
        self.connect_btn = wx.Button( self, wx.ID_ANY, "Connect", (500, 200), (100, 30), 0)

        self.start_btn = wx.Button(self, wx.ID_ANY, "start game", (390, 250), (100, 30), 0)
        self.stop_btn = wx.Button(self, wx.ID_ANY, "stop game", (500, 250), (100, 30), 0)

        self.status_static = wx.StaticText(self, -1, "", (390, 300), (200, 60), 0)

        self.digit_bmps = self.GetDigitBitmap()

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.count_time_event = None
        self.evt_count_time = None


        self.evt_turn_other = MyEvent(MyEvent.EVT_TURN_OTHER_TYPE, self.start_btn.GetId())
        self.evt_turn_me = MyEvent(MyEvent.EVT_TURN_ME_TYPE, self.stop_btn.GetId())

        self.InitSelectRobot()
        self.InitStopCtrl()


    def InitEvent(self):
        self.Bind(wx.EVT_BUTTON, self.OnListen, self.listen_btn)
        self.Bind(wx.EVT_BUTTON, self.OnConnect, self.connect_btn)

        self.Bind(wx.EVT_BUTTON, self.OnStart, self.start_btn)
        self.Bind(wx.EVT_BUTTON, self.OnStop, self.stop_btn)

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnStoneDown)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.timer_other = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer_other)


        CountTimeEvent, self.evt_count_time = wx.lib.newevent.NewCommandEvent()
        self.count_time_event = CountTimeEvent(self.GetId())
        self.Bind(self.evt_count_time, self.OnPaintTime)



        self.Bind(MyEvent.EVT_TURN_OTHER, self.OnTurnOther)

        self.Bind(MyEvent.EVT_TURN_ME, self.OnTurnMe)

    def InitSelectRobot(self):
        self.ip_addr.Show(False)
        self.ip_static_text.Show(False)

        self.port.Show(False)
        self.port_static_text.Show(False)

        self.listen_btn.Show(False)
        self.connect_btn.Show(False)

    def InitSelectNetwork(self):
        self.ip_addr.Show(True)
        self.ip_static_text.Show(True)

        self.port.Show(True)
        self.port_static_text.Show(True)

        self.listen_btn.Show(True)
        self.connect_btn.Show(True)

    def InitStartCtrl(self):
        self.robot_radio.Enable(False)
        self.network_radio.Enable(False)

        self.ip_addr.Enable(False)
        self.port.Enable(False)

        self.listen_btn.Enable(False)
        self.connect_btn.Enable(False)

        self.start_btn.Enable(False)
        self.stop_btn.Enable(True)


    def InitStopCtrl(self):
        self.robot_radio.Enable(True)
        self.network_radio.Enable(True)

        self.ip_addr.Enable(True)
        self.port.Enable(True)

        self.listen_btn.Enable(True)
        self.connect_btn.Enable(True)

        self.start_btn.Enable(True)
        self.stop_btn.Enable(False)


    def InitListenOrConnectCtrl(self):
        self.robot_radio.Enable(False)
        self.network_radio.Enable(False)

        self.ip_addr.Enable(False)
        self.port.Enable(False)

        self.listen_btn.Enable(False)
        self.connect_btn.Enable(False)

        self.start_btn.Enable(False)
        self.stop_btn.Enable(True)



    def GetDigitBitmap(self):
        digit_order = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        digit_bmps = []

        bmp = wx.Bitmap("%s/res/digit.bmp" %(cur_dir))
        bmp_height = bmp.Height / 12
        bmp_width = bmp.Width
        for seq in digit_order:
            digit_bmps.append(bmp.GetSubBitmap(wx.Rect(0, bmp_height * seq, bmp_width, bmp_height)))
        return digit_bmps


    def GetGridOrient(self, x, y):
        x_grid = int(round(x / GobangPanel.FACTOR))
        y_grid = int(round(y / GobangPanel.FACTOR))

        x_grid -= 1
        y_grid -= 1

        if 0 <= x_grid < GobangPanel.TOTAL_LINE_GRID and  0 <= y_grid < GobangPanel.TOTAL_LINE_GRID:
            return (x_grid, y_grid)
        return (None, None)


    def OnTimer(self, evt):
        self.count -= 1
        if self.count < 0:
            self.gobang.RandomStone(self.who_do)
            if self.robot_or_network == GobangPanel.ROBOT_OPT:
                if self.who_do == self.my_color:
                    self.GetEventHandler().ProcessEvent(self.evt_turn_other)
                else:
                    self.GetEventHandler().ProcessEvent(self.evt_turn_me)
            else:
                # TODO
                print "network"

        wx.PostEvent(self.GetEventHandler(), self.count_time_event)
        # wx.Post(self, self.count_time_event)

    def OnTurnOther(self, evt):
        print "turn other"
        self.who_do = not self.my_color

        # wx.PostEvent(self, wx.PyCommandEvent(wx.wxEVT_ERASE_BACKGROUND))

        self.timer_other.Stop()
        self.Refresh()

        self.count = GobangPanel.TIME_OUT
        self.timer_other.Start(1000)
        if self.robot_or_network == GobangPanel.ROBOT_OPT:
            self.gobang.RobotStone(self.who_do)
            self.Refresh()
            if self.who_do != self.my_color:
                print "============="
                self.GetEventHandler().ProcessEvent(self.evt_turn_me)


    def OnTurnMe(self, evt):
        print "turn me"
        self.who_do = self.my_color

        self.timer_other.Stop()
        self.count = GobangPanel.TIME_OUT

        # wx.PostEvent(self, wx.PyCommandEvent(wx.wxEVT_ERASE_BACKGROUND))
        self.Refresh()
        if self.robot_or_network == GobangPanel.ROBOT_OPT:
            self.timer_other.Start(1000)
            self.count = GobangPanel.TIME_OUT
        else:
            # TODO
            print "NETWORK"



    def RobotOrNetwork(self):
        # TODO
        print "hello"


    def OnClose(self, evt):
        self.timer.Close()
        self.timer.Destroy()

    def OnStoneDown(self, evt):
        if self.who_do != self.my_color or False == self.is_start:
            return

        pos = evt.GetPosition()
        (x_grid, y_grid) = self.GetGridOrient(pos.x, pos.y)
        if self.gobang.PutStone(x_grid, y_grid, self.who_do):
            if self.gobang.IsFive(x_grid, y_grid):
                wx.PostEvent(self.stop_btn.GetEventHandler(), EVT_BUTTON)

            self.GetEventHandler().ProcessEvent(self.evt_turn_other)
            self.Refresh()



    def OnRobotRadio(self, evt):
        self.robot_or_network = GobangPanel.ROBOT_OPT
        self.InitSelectRobot()


    def OnNetWorkRadio(self, evt):
        self.robot_or_network = GobangPanel.NETWORK_OPT
        self.InitSelectNetwork()


    def OnEraseBackground(self, evt):
        try:
            dc = e.GetDC()
        except:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)

        if False == self.is_start:
            dc.Clear()

        if None != self.who_do:
            print "%d brush" %(self.who_do)

        bmp = wx.Bitmap("res/bg.bmp")
        dc.DrawBitmap(bmp, 0, 0)

        for (key, stone) in self.gobang.stones.items():
            bmp = wx.Bitmap("res/blackstone.bmp" if Stone.WHITE == stone.color else "res/whitestone.bmp")
            dc.DrawBitmap(bmp, (stone.x_grid + 1) * GobangPanel.FACTOR, (stone.y_grid + 1) * GobangPanel.FACTOR)

        dc.DrawBitmap(self.digit_bmps[0 if self.count < 10 else self.count / 10], 400, 0)
        dc.DrawBitmap(self.digit_bmps[self.count % 10], 400 + self.digit_bmps[0].Width, 0)

    def OnPanitStone(self, evt):
        try:
            dc = evt.GetDC()
        except:
            dc = wx.ClientDC(self)

        if len(self.gobang.stack) > 0:
            stone = self.gobang.stack[-1]
            bmp = wx.Bitmap("res/blackstone.bmp" if Stone.WHITE == stone.color else "res/whitestone.bmp")
            dc.DrawBitmap(bmp, (stone.x_grid + 1) * GobangPanel.FACTOR, (stone.y_grid + 1) * GobangPanel.FACTOR)


    def OnPaintTime(self, evt):
        try:
            dc = evt.GetDC()
        except:
            dc = wx.ClientDC(self)

        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)

        dc.DrawBitmap(self.digit_bmps[0 if self.count < 10 else self.count / 10], 400, 0)
        dc.DrawBitmap(self.digit_bmps[self.count % 10], 400 + self.digit_bmps[0].Width, 0)

        if None == self.who_do:
            bmp = wx.Image("res/lights.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            dc.DrawBitmap(bmp, 450, 0)
        elif self.my_color == self.who_do:
            bmp = wx.Image("res/green.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            dc.DrawBitmap(bmp, 450, 0)
        else:
            bmp = wx.Image("res/red.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            dc.DrawBitmap(bmp, 450, 0)


    def EnableOrDisableCtrl(self, status):
        self.listen_btn.Disable(status)
        self.connect_btn.Disable(status)
        self.network_radio.Disable(status)
        self.robot_radio.Disable(status)


    def OnListen(self, evt):
        ip = self.ip_addr.GetValue()
        port = self.port.GetValue()
        self.network = GobangServer(ip, port, self)
        self.network.start()

        self.InitListenOrConnectCtrl()

        self.status_static.SetLabel("listening ....")



    def OnConnect(self, evt):
        ip = self.ip_addr.GetValue()
        port = self.port.GetValue()
        self.network = GobangClient(ip, port, self)
        self.network.start()

        self.status_static.SetLabel("connect ...")

    def OnStart(self, evt):
        self.InitStartCtrl()

        if GobangPanel.ROBOT_OPT == self.robot_or_network:
            self.my_color = Gobang.RandomOrder()
            self.who_do = Stone.WHITE

            self.is_start = True

            if self.who_do == self.my_color:
                self.evt_turn_me.set_args(None)
                self.GetEventHandler().ProcessEvent(self.evt_turn_me)
            else:
                self.evt_turn_other.set_args(None)
                self.GetEventHandler().ProcessEvent(self.evt_turn_other)


    def OnStop(self, evt):
        self.InitStopCtrl()

        self.who_do = None
        self.my_color = None
        self.timer_other.Stop()
        self.count = GobangPanel.TIME_OUT
        self.is_start = False

        wx.PostEvent(self.GetEventHandler(), self.count_time_event)
