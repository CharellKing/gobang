#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys

import wx
import wx.lib.newevent
import socket, select

import traceback

from module_msg import ModuleMsg
from cmd_controller import CmdController, CmdMsg
from gobang import Gobang, Stone

cur_dir = os.path.split(os.path.realpath(__file__))[0]

CountTimeEvent, EVT_COUNT_TIME = wx.lib.newevent.NewEvent()
PutStoneEvent, EVT_PUT_STONE = wx.lib.newevent.NewEvent()

class GuiPanel(wx.Panel):
    FACTOR = 24.0
    GRID_SIZE = 24

    def __init__(self, parent, cmd_controller):
        self.frame = parent

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


        self.cmd_controller = cmd_controller
        self.cmd_controller.set_thread_func(self.work_thread)

        self.InitCtrl(parent)
        self.InitEvent()

    def InitCtrl(self, parent):
        wx.Panel.__init__(self, parent=parent)

        self.robot_radio = wx.RadioButton( self, wx.ID_ANY, "robot", (390, 100), (80, 30), 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRobotRadio, self.robot_radio)

        self.network_radio = wx.RadioButton( self, wx.ID_ANY, "network", (530, 100), (80, 30), 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnNetworkRadio, self.network_radio)

        self.ip_static_text = wx.StaticText(self, -1, "ip:", pos = (390, 150), size = (15, 30), style = wx.ALL)
        self.ip_addr = wx.TextCtrl(self, -1, "127.0.0.1", (420, 150), (80, 30), style = wx.ALL)

        self.port_static_text = wx.StaticText(self, -1, "port:", pos = (510, 150), size = (30, 30), style = wx.ALL)
        self.port = wx.TextCtrl(self, -1, "8889", (550, 150), (50, 30), style = wx.ALL)

        self.listen_btn = wx.Button( self, wx.ID_ANY, "Listen", (390, 200), (100, 30), 0)
        self.connect_btn = wx.Button( self, wx.ID_ANY, "Connect", (500, 200), (100, 30), 0)

        self.start_btn = wx.Button(self, wx.ID_ANY, "start game", (390, 250), (100, 30), 0)
        self.stop_btn = wx.Button(self, wx.ID_ANY, "stop game", (500, 250), (100, 30), 0)

        self.status_static = wx.StaticText(self, -1, "", (390, 300), (200, 60), 0)

        self.digit_bmps = self.GetDigitBitmap()

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.count_time_event = None
        self.evt_count_time = None


        wx.PostEvent(self.robot_radio, wx.PyCommandEvent(wx.EVT_RADIOBUTTON.typeId, self.robot_radio.GetId()))



    def InitEvent(self):
        self.Bind(wx.EVT_BUTTON, self.OnListen, self.listen_btn)
        self.Bind(wx.EVT_BUTTON, self.OnConnect, self.connect_btn)

        self.Bind(wx.EVT_BUTTON, self.OnStart, self.start_btn)
        self.Bind(wx.EVT_BUTTON, self.OnStop, self.stop_btn)

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnStoneDown)


        self.Bind(EVT_COUNT_TIME, self.OnPaintTime)
        self.Bind(EVT_PUT_STONE, self.OnPaintStone)

    def InitSelectRobot(self):
        print "Init Select Robot"
        self.ip_addr.Show(False)
        self.ip_static_text.Show(False)

        self.port.Show(False)
        self.port_static_text.Show(False)

        self.listen_btn.Show(False)
        self.connect_btn.Show(False)

        print "2:start btn True"
        self.start_btn.Enable(True)
        print "3: stop btn False"
        self.stop_btn.Enable(False)

    def InitSelectNetwork(self):
        print "Init Select Network"
        self.ip_addr.Show(True)
        self.ip_static_text.Show(True)

        self.port.Show(True)
        self.port_static_text.Show(True)

        self.listen_btn.Show(True)
        self.connect_btn.Show(True)

        print "3:start btn False"
        self.start_btn.Enable(False)
        print "4: stop btn False"
        self.stop_btn.Enable(False)

    def InitStartCtrl(self):
        self.robot_radio.Enable(False)
        self.network_radio.Enable(False)

        self.ip_addr.Enable(False)
        self.port.Enable(False)

        self.listen_btn.Enable(False)
        self.connect_btn.Enable(False)

        print "4:start btn False"
        self.start_btn.Enable(False)
        print "5: stop btn True"
        self.stop_btn.Enable(True)


    def InitStopCtrl(self):
        self.robot_radio.Enable(True)
        self.network_radio.Enable(True)

        self.ip_addr.Enable(True)
        self.port.Enable(True)

        self.listen_btn.Enable(True)
        self.connect_btn.Enable(True)


        if CmdController.NETPLAY_MODE == self.cmd_controller.mode:
            print "1:start btn False"
            self.start_btn.Enable(False)
            print "1:start btn True"
        elif CmdController.ROBOTPLAY_MODE == self.cmd_controller.mode:
            self.start_btn.Enable(True)

        print "1: stop btn false"
        self.stop_btn.Enable(False)

        # if self.cmd_controller.is_starting():
        wx.PostEvent(self, wx.PyCommandEvent(wx.wxEVT_ERASE_BACKGROUND))
        wx.PostEvent(self.GetEventHandler(), CountTimeEvent())



    def InitListenOrConnectCtrl(self):
        self.robot_radio.Enable(False)
        self.network_radio.Enable(False)

        self.ip_addr.Enable(False)
        self.port.Enable(False)

        self.listen_btn.Enable(False)
        self.connect_btn.Enable(False)

        self.start_btn.Enable(True)
        print "2: stop_btn True"
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
        x_grid = int(round(x / GuiPanel.FACTOR))
        y_grid = int(round(y / GuiPanel.FACTOR))

        x_grid -= 1
        y_grid -= 1

        if 0 <= x_grid < Gobang.GRIDS and  0 <= y_grid < Gobang.GRIDS:
            return (x_grid, y_grid)
        return (None, None)



    def OnClose(self, evt):
        print "OnClose"
        if True == self.cmd_controller.is_starting():
            print "before tip"
            dlg = wx.MessageDialog(None, "您正处于游戏中, 是否要离开", '提示', wx.YES_NO | wx.ICON_INFORMATION)
            print "After tip"
            if dlg.ShowModal() == wx.ID_YES:
                print "on close exit"
                self.cmd_controller.exit_without_promt(CmdMsg("exit"))
            dlg.Destroy()
        else:
            print "on close exit"
            self.cmd_controller.exit_without_promt(CmdMsg("exit"))


    def OnRobotRadio(self, evt):
        if True == self.cmd_controller.is_starting():
            dlg = wx.MessageDialog(None, "您正在游戏中,是否离开?", '提示', wx.YES_NO | wx.ICON_INFORMATION)
            if dlg.ShowModal() == wx.ID_YES:
                self.InitSelectRobot()
                self.cmd_controller.join_mode_without_promt(CmdMsg("join_mode 人机对弈"))
        else:
            self.InitSelectRobot()
            self.cmd_controller.join_mode_without_promt(CmdMsg("join_mode 人机对弈"))




    def OnNetworkRadio(self, evt):
        if True == self.cmd_controller.is_starting():
            dlg = wx.MessageDialog(None, "您正在游戏中,是否离开?", '提示', wx.YES_NO | wx.ICON_INFORMATION)
            if dlg.ShowModal() == wx.ID_YES:
                self.InitSelectNetwork()
                self.cmd_controller.join_mode_without_promt(CmdMsg("join_mode 网络对弈"))

        else:
            print "InitSelectNetwork"
            self.InitSelectNetwork()
            self.cmd_controller.join_mode_without_promt(CmdMsg("join_mode 网络对弈"))



    def OnEraseBackground(self, evt):
        # dc = wx.ClientDC(self)
        # rect = self.GetUpdateRegion().GetBox()
        # dc.SetClippingRect(rect)

        dc = wx.ClientDC(self)
        rect = wx.Rect(0, 0, GuiPanel.FACTOR * (Gobang.GRIDS + 1), GuiPanel.FACTOR * (Gobang.GRIDS + 1))
        dc.SetClippingRect(rect)


        dc.Clear()
        bmp = wx.Bitmap("res/bg.bmp")
        dc.DrawBitmap(bmp, 0, 0)

        wx.PostEvent(self.GetEventHandler(), CountTimeEvent())
        wx.PostEvent(self.GetEventHandler(), PutStoneEvent())

        # if False == self.cmd_controller.is_starting():
        #     rect = wx.Rect(0, 0, GuiPanel.FACTOR * Gobang.GRIDS, GuiPanel.FACTOR * Gobang.GRIDS)
        #     dc.SetClippingRect(rect)

        #     dc.Clear()

        #     bmp = wx.Bitmap("res/bg.bmp")
        #     dc.DrawBitmap(bmp, 0, 0)

        #     if None != self.cmd_controller.roles[0] and None != self.cmd_controller.roles[0].time:
        #         count = self.cmd_controller.roles[0].time
        #         print "xxxxxxxxxxxxxxxxxcount = ", count
        #         dc.DrawBitmap(self.digit_bmps[0 if count < 10 else count / 10], 400, 0)
        #         dc.DrawBitmap(self.digit_bmps[count % 10], 400 + self.digit_bmps[0].Width, 0)








    def OnPaintStone(self, evt):
        dc = wx.ClientDC(self)
        rect = wx.Rect(0, 0, GuiPanel.FACTOR * (Gobang.GRIDS + 1), GuiPanel.FACTOR * (Gobang.GRIDS + 1))
        dc.SetClippingRect(rect)


        if self.cmd_controller.is_starting():
            dc.Clear()
            bmp = wx.Bitmap("res/bg.bmp")
            dc.DrawBitmap(bmp, 0, 0)

            human_role = self.cmd_controller.roles[0]
            for stone in human_role.gobang.stones.values():
                bmp = wx.Bitmap("res/blackstone.bmp" if Stone.BLACK == stone.color else "res/whitestone.bmp")
                dc.DrawBitmap(bmp, (stone.x_grid) * GuiPanel.FACTOR + GuiPanel.FACTOR / 2, (stone.y_grid) * GuiPanel.FACTOR + GuiPanel.FACTOR / 2)

        # if self.cmd_controller.is_starting():
        #     human_role = self.cmd_controller.roles[0]
        #     if len(human_role.gobang.stack) > 0:
        #         stone = human_role.gobang.stack[-1]
        #         bmp = wx.Bitmap("res/blackstone.bmp" if Stone.WHITE == stone.color else "res/whitestone.bmp")
        #         dc.DrawBitmap(bmp, (stone.x_grid + 1) * GuiPanel.FACTOR, (stone.y_grid + 1) * GuiPanel.FACTOR)


    def OnPaintTime(self, evt):
        dc = wx.ClientDC(self)
        rect = self.GetUpdateRegion().GetBox()
        dc.SetClippingRect(rect)


        if self.cmd_controller.is_starting():
            human_role = self.cmd_controller.roles[0]
            dc.DrawBitmap(self.digit_bmps[0 if human_role.time < 10 else human_role.time / 10], 400, 0)
            dc.DrawBitmap(self.digit_bmps[human_role.time % 10], 400 + self.digit_bmps[0].Width, 0)
        else:
            dc.DrawBitmap(self.digit_bmps[0 if Gobang.RELAY_TIME < 10 else Gobang.RELAY_TIME / 10], 400, 0)
            dc.DrawBitmap(self.digit_bmps[Gobang.RELAY_TIME % 10], 400 + self.digit_bmps[0].Width, 0)



        if None == self.cmd_controller.roles[0] or None == self.cmd_controller.roles[0].status:
            bmp = wx.Image("res/lights.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            dc.DrawBitmap(bmp, 450, 0)
        elif "GO" == self.cmd_controller.roles[0].status:
            bmp = wx.Image("res/green.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            dc.DrawBitmap(bmp, 450, 0)
        elif "WAIT" == self.cmd_controller.roles[0].status:
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

        if True == self.cmd_controller.is_starting():
            self.status_static.SetLabel("游戏正进行中")
        elif CmdController.ROBOTPLAY_MODE == self.cmd_controller.mode:
            self.status_static.SetLabel("您正处于[%s]模式" %(self.cmd_controller.mode))
        else:
            self.status_static.SetLabel("listening ....")
            if False == self.cmd_controller.hold_without_promt(CmdMsg("hold %s" %(port))):
                self.status_static.SetLabel("端口不正确")




    def OnConnect(self, evt):
        ip = self.ip_addr.GetValue()
        port = self.port.GetValue()

        if True == self.cmd_controller.is_starting():
            self.status_static.SetLabel("游戏正进行中")
        elif CmdController.ROBOTPLAY_MODE == self.cmd_controller.mode:
            self.status_static.SetLabel("您正处于[%s]模式" %(self.cmd_controller.mode))
        else:
            self.status_static.SetLabel("connect ....")
            if False == self.cmd_controller.attent_without_promt(CmdMsg("attent %s %s" %(ip, port))):
                self.status_static.SetLabel("ip或者端口不正确")


    def OnStart(self, evt):
        if CmdController.NETPLAY_MODE == self.cmd_controller.mode and False == self.cmd_controller.is_net_running():
            self.status_static.SetLabel("您处于%s模式, 对弈双方网络连接还没有连接起来" %(self.cmd_controller.mode))
        elif self.cmd_controller.is_starting():
            self.status_static.SetLabel("您已经在游戏中了")
        else:
            self.InitStartCtrl()
            self.cmd_controller.start_game_without_promt(CmdMsg("start_game"))


    def OnStop(self, evt):
        if True == self.cmd_controller.is_starting():
            dlg = wx.MessageDialog(None, "是否停止游戏", '提示', wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            if result == wx.ID_YES:
                self.InitStopCtrl()
                self.cmd_controller.stop_game_without_promt(CmdMsg("stop_game"))
            dlg.Destroy()
        else:
            self.InitStopCtrl()
            self.cmd_controller.stop_game_without_promt(CmdMsg("stop_game"))


    def OnStoneDown(self, evt):
        if self.cmd_controller.is_starting():
            if "GO" == self.cmd_controller.roles[0].status:
                pos = evt.GetPosition()
                (x_grid, y_grid) = self.GetGridOrient(pos.x, pos.y)
                if None != x_grid and None != y_grid and \
                  False == self.cmd_controller.roles[0].gobang.is_taken_up(x_grid, y_grid):
                    self.cmd_controller.put_down_without_promt(CmdMsg("put_down %d %d" %(x_grid, y_grid)))
                else:
                    self.status_static.SetLabel("此位置已经被占")
            else:
                self.status_static.SetLabel("请等待")
        else:
            self.status_static.SetLabel("游戏还没开始")


    def recv_msg(self, msg):
        if ModuleMsg.PROMT_LOG_MSG_TYPE == msg.msg_type:
            wx.CallAfter(self.status_static.SetLabel,"%s" %(msg.content[0]))
        elif ModuleMsg.THREAD_EXIT_MSG_TYPE == msg.msg_type:
            self.InitStopCtrl()
            wx.CallAfter(self.status_static.SetLabel,"stop msg")
            # wx.PostEvent(self, wx.PyCommandEvent(wx.wxEVT_ERASE_BACKGROUND))
            self.cmd_controller.thread_is_exit = True
        elif ModuleMsg.LISTEN_SUCC_MSG_TYPE == msg.msg_type:
            self.InitListenOrConnectCtrl()
            wx.CallAfter(self.status_static.SetLabel,"listen success")
        elif ModuleMsg.LISTEN_ERR_MSG_TYPE == msg.msg_type:
            wx.CallAfter(self.status_static.SetLabel,"listen error")
        elif ModuleMsg.CONNECT_SUCC_MSG_TYPE == msg.msg_type:
            self.InitListenOrConnectCtrl()
            wx.CallAfter(self.status_static.SetLabel,"connect success")
        elif ModuleMsg.CONNECT_ERR_MSG_TYPE == msg.msg_type:
            wx.CallAfter(self.status_static.SetLabel,"connect error")
        elif ModuleMsg.SRV_RECV_CONN_MSG_TYPE == msg.msg_type:
            wx.CallAfter(self.status_static.SetLabel,"other's connect me")
        elif ModuleMsg.PUT_MSG_TYPE == msg.msg_type:
            wx.PostEvent(self.GetEventHandler(), CountTimeEvent())
            wx.PostEvent(self.GetEventHandler(), PutStoneEvent(msg = msg))
        elif ModuleMsg.TIME_MSG_TYPE == msg.msg_type:
            wx.PostEvent(self.GetEventHandler(), CountTimeEvent())
        elif ModuleMsg.STOP_MSG_TYPE == msg.msg_type:
            self.InitStopCtrl()
            (ret, x_grid, y_grid, color) = msg.content
            if None != x_grid and None != y_grid:
                wx.PostEvent(self.GetEventHandler(), PutStoneEvent(msg = ModuleMsg(ModuleMsg.PUT_MSG_TYPE, [color, x_grid, y_grid])))


            msg_text = {Gobang.TIED: "你俩打平了", Gobang.SUCCESS: "你赢了", Gobang.FAILED: "你输了", Gobang.UNKNOWN: "游戏终止被终止"}
            wx.CallAfter(self.status_static.SetLabel, msg_text[ret])

        elif ModuleMsg.EXIT_MSG_TYPE == msg.msg_type:
            print "hello"
            self.InitStopCtrl()
            print "some one exit"
            wx.CallAfter(self.status_static.SetLabel,"some one exit")
            self.cmd_controller.thread_is_exit = True




    def work_thread(self):
        inputs = [self.cmd_controller.interface_in]
        timeout = 1
        self.cmd_controller.thread_is_exit = False
        while False == self.cmd_controller.thread_is_exit:
            readable, writable, exceptional = select.select(inputs, [], inputs, timeout)
            if readable or writable or exceptional:
                for fd in readable:
                    if fd is self.cmd_controller.interface_in:
                        msg_strs = os.read(fd, ModuleMsg.MAX_MSG_LEN).split('\n')
                        for msg_str in msg_strs:
                            if "" != msg_str:
                                msg = ModuleMsg().decode(msg_str)
                                self.recv_msg(msg)


        for role in self.cmd_controller.roles:
            role.work.join()

        self.cmd_controller.roles = [None, None]
