#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys


import socket, select
from threading import Thread
from gobang_msg import GobangMsg


class GobangServer(object):
    def __init__(self, host, port, net_in, net_out):
        self.host = host
        self.port = int(port)
        self.svr_sock = None
        self.conn_sock = None

        self.is_exit = False


    def WorkerThread(self):
        inputs = [net_in, self.svr_sock]
        outputs = []
        timeout = None

        while inputs and False == self.is_exit:
            readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
            if readable or writable or exceptional:
                for sock in readable:
                    if sock is self.svr_sock:
                        timeout = 1
                        self.conn_sock, client_address = sock.accept()
                        self.conn.setblocking(0)
                        inputs.append(self.conn)

                    else:
                        data = sock.recv(1024)
                        for pack in data.split("###"):
                            if pack and len(pack) > 0:
                                msg = GobangMsg()
                                msg.decode(pack)

                                if msg.type == GobangMsg.START_MSG_TYPE:
                                    wx.CallAfter(self.gui.OtherStart)

                                elif msg.type == GobangMsg.TURN_ON_OTHER:
                                    self.gui.evt_turn_me.set_args((msg.content[0], msg.content[1]))
                                    self.gui.GetEventHandler().ProcessEvent(self.gui.evt_turn_me)

                                elif msg.type == GobangMsg.TIMEOUT_MSG_TYPE:
                                    wx.CallAfter(self.gui.recv_time_out, msg.content[0], msg.content[1])

                                elif msg.type == GobangMsg.TIMER_MSG_TYPE:
                                    wx.CallAfter(self.gui.recv_timer, msg.content[0])
                                elif msg.type == GobangMsg.RESULT_MSG_TYPE:
                                    wx.CallAfter(self.gui.Result, msg.content[0])
                for sock in exceptional:
                    inputs.remove(sock)
                    if sock in outputs:
                        outputs.remove(sock)



        wx.PostEvent(self.gui.stop_btn, wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.gui.stop_btn.GetId()))
        if None != self.sock:
            self.sock.close()
        if None != self.conn:
            self.conn.close()

    def start(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.host, self.port))
            self.sock.listen(1)
            self.is_start = True
            worker = Thread(target = self.WorkerThread, args = (self.sock,))
            worker.start()
            return True
        except Exception, ex:
            self.gui.status_static.SetLabel("listen failed!!!!!")
            print Exception, ":", ex
            return False


    def stop(self):
        self.is_start = False
        if None != self.conn:
            self.conn.close()
            self.conn = None
        if None != self.sock:
            self.sock.close()
            self.sock = None

    def send(self, msg):
        if None != self.conn:
            self.conn.send(msg.encode() + '###')


class GobangClient(object):
    IS_LISTENER = False

    def __init__(self, host, port, gui):
        self.host = host
        self.port = int(port)
        self.sock = None
        self.gui = gui

        self.is_start = False

    def WorkerThread(self, args):
        (cli_sock) = args
        inputs = [cli_sock]
        outputs = [cli_sock]
        timeout = 1

        while inputs and self.is_start:
            readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
            if (readable or writable or exceptional):
                for sock in readable:
                    data = sock.recv(1024)
                    for pack in data.split("###"):
                        if pack and len(pack) > 0:
                            msg = GobangMsg()
                            msg.decode(pack)

                            if msg.type == GobangMsg.START_MSG_TYPE:
                                wx.CallAfter(self.gui.OtherStart)

                            elif msg.type == GobangMsg.TURN_ON_OTHER:
                                self.gui.evt_turn_me.set_args((msg.content[0], msg.content[1]))
                                self.gui.GetEventHandler().ProcessEvent(self.gui.evt_turn_me)

                            elif msg.type == GobangMsg.TIMEOUT_MSG_TYPE:
                                wx.CallAfter(self.gui.recv_time_out, msg.content[0], msg.content[1])

                            elif msg.type == GobangMsg.TIMER_MSG_TYPE:
                                wx.CallAfter(self.gui.recv_timer, msg.content[0])

                            elif msg.type == GobangMsg.START_GAME_MSG_TYPE:
                                wx.CallAfter(self.gui.recv_start_game, msg.content[0])
                            elif msg.type == GobangMsg.RESULT_MSG_TYPE:
                                    wx.CallAfter(self.gui.Result, msg.content[0])

            for s in exceptional:
                inputs.remove(s)
                if s in outputs:
                    outputs.remove(s)



        wx.PostEvent(self.gui.stop_btn, wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.gui.stop_btn.GetId()))
        self.sock.close()
        self.sock = None

    def start(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.gui.status_static.SetLabel("connect success")
            self.is_start = True
            worker = Thread(target = self.WorkerThread, args = (self.sock, ))
            worker.start()
            return True
        except Exception, ex:
            self.gui.status_static.SetLabel("connect failed!!!!!")
            print Exception, ":", ex
            return False


    def stop(self):
        self.is_start = False
        self.sock.close()

    def send(self, msg):
        self.sock.send(msg.encode())
