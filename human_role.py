#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys
from threading import Thread
import socket, select

from module_msg import ModuleMsg
from gobang import Gobang, Stone

class HumanRole(object):
    def __init__(self, human_in, human_out, human_interface_out):
        self.fin= human_in
        self.out = human_out
        self.interface_out = human_interface_out

        self.timeout = None

        self.work = None
        self.is_exit = True
        self.color = None
        self.status = None
        self.time = None
        self.gobang = None

        self.is_start = False


    def send_color_msg(self):
        ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human send color msg"]).send(self.interface_in)

        self.color = Gobang.random_order()
        self.gobang = Gobang()
        ModuleMsg(ModuleMsg.COLOR_MSG_TYPE, [not self.color]).send(self.out)
        if self.color == Stone.WHITE:
            self.status = "GO"
        else:
            self.status = "WAIT"
        self.time = Gobang.RELAY_TIME


    def recv_color_msg(self, msg):
        ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human recv color msg"]).send(self.interface_in)

        color = msg.content[0]
        self.is_start = True
        self.color = color
        if Stone.WHITE == color:
            self.status = "GO"
        else:
            self.status = "WAIT"

    def send_start_msg(self):
        ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human send start msg"]).send(self.interface_in)

        self.gobang = Gobang()
        self.is_start = True
        ModuleMsg(ModuleMsg.START_MSG_TYPE).send(self.out)

    def recv_start_msg(self, msg):
        ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human recv start_msg"]).send(self.interface_in)

        if True == self.is_start:
            self.send_color_msg()
        else:
            ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human: wait other's start"]).send(self.interface_in)

    def send_putdown_msg(self, x_grid, y_grid):
        ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human send putdown (%d %d) msg" %(x_grid, y_grid)]).send(self.interface_in)

        self.gobang.put_stone(x_grid, y_grid, self.color)
        ModuleMsg(ModuleMsg.PUT_MSG_TYPE, [self.color, x_grid, y_grid]).send(self.out)
        self.status = "WAIT"
        self.time = Gobang.RELAY_TIME

        justy_result(x_grid, y_grid)

    def justy_result(self, x_grid, y_grid):
        ret = Gobang.UNKNOWN
        if True == self.gobang.is_tie(x_grid, y_grid):
            ret = Gobang.TIED
        if True == self.gobang.is_five(x_grid, y_grid):
            ret = Gobang.SUCCESS

        if Gobang.UNKNOWN != ret:
            self.send_exit_msg(ret)


    def recv_putdown_msg(self, msg):
        ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human recv put down (%d %d) msg" %(x_grid, y_grid)]).send(self.interface_in)

        (color, x_grid, y_grid) = msg.content

        self.gobang.put_stone(x_grid, y_grid, color)
        self.status = "GO"
        self.time = Gobang.RELAY_TIME

    def send_time_msg(self):
        if self.time > 0:
            ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human: send time msg"]).send(self.interface_in)
            self.time -= 1
            msg = ModuleMsg(ModuleMsg.TIME_MSG_TYPE, [self.time])
        else:
            (x_grid, y_grid) = self.gobang.random_stone(self.color)
            ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human: send timeout (%d %d) msg" %(x_grid, y_grid)]).send(self.interface_in)

            ModuleMsg(ModuleMsg.PUT_MSG_TYPE, [self.color, x_grid, y_grid]).send(self.out)

            self.status = "WAIT"
            self.time = Gobang.RELAY_TIME

            self.justy_result(x_grid, y_grid)

    def recv_time_msg(self, msg):
        time = msg.content[0]
        ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human: recv time (%d) msg" %(time)]).send(self.interface_in)
        self.time = time


    def send_exit_msg(self, ret):
        self.is_exit = True
        ModuleMsg(ModuleMsg.EXIT_MSG_TYPE, [ret]).send(self.out)


    def recv_exit_msg(self, msg):
        self.is_exit = True
        self.work_thread.join()

    def recv_msg(self, msg):
        if msg.msg_type == ModuleMsg.START_MSG_TYPE:
            self.recv_start_msg(msg)
        elif msg.msg_type == ModuleMsg.COLOR_MSG_TYPE:
            self.recv_color_msg(msg)
        elif msg.msg_type == ModuleMsg.PUT_MSG_TYPE:
            self.recv_putdown_msg(msg)
        elif msg.msg_type == ModuleMsg.TIME_MSG_TYPE:
            self.recv_time_msg(msg)
        elif msg.msg_type == ModuleMsg.EXIT_MSG_TYPE:
            self.recv_exit_msg()
        else:
            ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["无效的消息"]).send(self.interface_in)

    def work_thread(self):
        inputs = [self.fin]
        outputs = []
        timeout = 1

        self.is_exit = False
        while False == self.is_exit:
            readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
            if readable or writable or exceptional:
                for fd in readable:
                    if fd is self.fin:
                            msg = ModuleMsg().recv(fd)
                            self.recv_msg(msg)
            elif "GO" == self.status and False == self.is_exit:
                self.send_time_msg()

    def start(self):
        self.work = Thread(target = self.work_thread)
        self.work.start()
