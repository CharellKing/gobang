#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys

from threading import Thread
import socket, select


from module_msg import ModuleMsg
from gobang import Gobang, Stone

class RobotRole(object):
    def __init__(self, robot_in, robot_out):
        self.fin = robot_in
        self.out = robot_out
        self.timeout = None

        self.work = None
        self.thread_is_exit = True
        self.color = None
        self.status = None
        self.time = None
        self.gobang = None


    def recv_start_msg(self, msg):
        self.color = Gobang.random_order()
        self.gobang = Gobang()
        msg = ModuleMsg(ModuleMsg.COLOR_MSG_TYPE, [not self.color]).send(self.out)

        if self.color == Stone.WHITE:
            print "robot_go"
            self.status = "GO"
            self.recv_putdown_msg(ModuleMsg(ModuleMsg.PUT_MSG_TYPE, [None, None, None]))
        else:
            print "robot_wait"
            self.status = "WAIT"
        self.time = Gobang.RELAY_TIME

    def recv_putdown_msg(self, msg):
        (color, x_grid, y_grid) = msg.content
        (put_x_grid, put_y_grid) = (Gobang.GRIDS >> 1, Gobang.GRIDS >> 1)
        if None == x_grid and None == y_grid:
            self.gobang.put_stone(put_x_grid, put_y_grid, self.color)
        else:
            self.gobang.put_stone(x_grid, y_grid, color)
            (put_x_grid, put_y_grid) = self.gobang.random_stone(self.color)
        self.status = "WAIT"
        ModuleMsg(ModuleMsg.PUT_MSG_TYPE, [self.color, put_x_grid, put_y_grid]).send(self.out)
        self.time = Gobang.RELAY_TIME
        self.justy_result(put_x_grid, put_y_grid)


    def justy_result(self, x_grid, y_grid):
        ret = Gobang.UNKNOWN
        if True == self.gobang.is_tie(x_grid, y_grid):
            ret = Gobang.TIED
        if True == self.gobang.is_five(x_grid, y_grid):
            ret = Gobang.FAILED    #发送给对方，对方失败了

        if Gobang.UNKNOWN != ret:
            self.send_stop_msg(ret, x_grid, y_grid)
        return ret


    def recv_time_msg(self, msg):
        time = msg.content[0]
        self.time = time

    def recv_thread_exit_msg(self, msg):
        self.thread_is_exit = True

    def send_thread_exit_msg(self):
        ModuleMsg(ModuleMsg.THREAD_EXIT_MSG_TYPE).send(self.out)
        self.thread_is_exit = True


    def recv_stop_msg(self, msg):
        (ret, x_grid, y_grid, color) = msg.content
        if None != x_grid and None != y_grid:
            self.gobang.put_stone(x_grid, y_grid, color)
        self.status = None

    def send_stop_msg(self, ret, x_grid = None, y_grid = None):
        ModuleMsg(ModuleMsg.STOP_MSG_TYPE, [ret, x_grid, y_grid, self.color]).send(self.out)
        self.status = None

    def recv_exit_msg(self, msg):
        self.thread_is_exit = True

    def send_exit_msg(self):
        ModuleMsg(ModuleMsg.EXIT_MSG_TYPE).send(self.out)
        self.thread_is_exit = True
        self.status = None


    def recv_msg(self, msg):
        if msg.msg_type == ModuleMsg.START_MSG_TYPE:
            self.recv_start_msg(msg)
        elif msg.msg_type == ModuleMsg.PUT_MSG_TYPE:
            self.recv_putdown_msg(msg)
        elif msg.msg_type == ModuleMsg.TIME_MSG_TYPE:
            self.recv_time_msg(msg)
        elif msg.msg_type == ModuleMsg.THREAD_EXIT_MSG_TYPE:
            self.recv_thread_exit_msg(msg)
        elif msg.msg_type == ModuleMsg.EXIT_MSG_TYPE:
            self.recv_exit_msg(msg)

    def send_time_out(self, msg):
        if self.time > 0:
            self.time -= 1
            msg = ModuleMsg(ModuleMsg.TIME_MSG_TYPE, [self.time])
        else:
            self.time = Gobang.RELAY_TIME
            self.status = "WAIT"
            (x_grid, y_grid) = self.gobang.random_stone(self.color)

            if Gobang.UNKNOWN == self.justy_result(x_grid, y_grid):

                ModuleMsg(ModuleMsg.PUT_MSG_TYPE, [self.color, x_grid, y_grid]).send(out)


    def work_thread(self):
        inputs = [self.fin]
        outputs = []
        timeout = 1

        self.thread_is_exit = False
        while False == self.thread_is_exit:
            readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
            if readable or writable or exceptional:
                for fd in readable:
                    if fd is self.fin:
                        msg_strs = os.read(fd, ModuleMsg.MAX_MSG_LEN).split('\n')
                        for msg_str in msg_strs:
                            if "" != msg_str:
                                msg = ModuleMsg().decode(msg_str)
                                self.recv_msg(msg)

            elif "GO" == self.status and False == self.thread_is_exit:
                self.send_time_out(msg)


    def start(self):
        self.work = Thread(target = self.work_thread)
        self.work.start()
