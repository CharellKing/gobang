#!/usr/bin/python

import socket, select
from threading import Thread
import Queue
import signal
from gobang_msg import GobangMsg
import wx

class GobangServer(object):
    IS_LISTENER = True

    def __init__(self, host, port, gui):
        self.host = host
        self.port = int(port)
        self.message_queues = {}
        self.gui = gui
        self.is_start = False
        self.sock = None
        self.conn = None


    def WorkerThread(self, args):
        (svr_sock) = args
        inputs = [svr_sock]
        outputs = []
        timeout = 1

        while inputs and self.is_start:
            readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)

            if readable or writable or exceptional:
                for sock in readable:
                    if sock is svr_sock:
                        timeout = 1
                        self.conn, client_address = sock.accept()
                        wx.CallAfter(self.gui.status_static.SetLabel, "%s connected" %(client_address[0]))
                        # self.gui.status_static.SetLabel("%s connected" %(client_address[0]))
                        self.conn.setblocking(0)
                        inputs.append(self.conn)
                        # conn.send()
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



        wx.PostEvent(self.gui.stop_btn, wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.gui.stop_btn.GetId()))
        if None != self.sock:
            self.sock.close()
        if None != self.conn:
            self.conn.close()

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)

        self.is_start = True
        worker = Thread(target = self.WorkerThread, args = (self.sock,))
        worker.start()

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


        wx.PostEvent(self.gui.stop_btn, wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.gui.stop_btn.GetId()))
        self.sock.close()
        self.sock = None

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.gui.status_static.SetLabel("connect success")
        self.is_start = True
        worker = Thread(target = self.WorkerThread, args = (self.sock, ))
        worker.start()

    def stop(self):
        self.is_start = False
        self.sock.close()

    def send(self, msg):
        self.sock.send(msg.encode())
