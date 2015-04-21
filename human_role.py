#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys
from threading import Thread
import socket, select

from module_msg import ModuleMsg

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


    def send_start_msg(self):
        self.is_start = True
        print self.out
        ModuleMsg(ModuleMsg.START_MSG_TYPE).send(self.out)
        print "hello"

    def deal_start_msg(self):
        if True == self.is_start:
            self.color = Gobang.RandomOrder()
            self.gobang = Gobang()
            ModuleMsg(ModuleMsg.COLOR_MSG_TYPE, [not self.color]).send(self.out)
            if self.color == GobangStone.WHITE:
                self.status = "GO"
            else:
                self.status = "WAIT"
            self.time = Gobang.RELAY_TIME

    def send_putdown_msg(self, x_grid, y_grid):
        self.gobang.put_stone(x_grid, y_grid, self.color)
        ModuleMsg(ModuleMsg.PUT_MSG_TYPE, [self.color, x_grid, y_grid]).send(self.out)

    def deal_putdown_msg(self, color, x_grid, y_grid):
        self.gobang.put_stone(x_grid, y_grid, color)
        self.status = "GO"
        self.time = Gobang.RELAY_TIME

    def send_time_msg(self):
        ModuleMsg(ModuleMsg.TIME_MSG_TYPE, [self.time]).send(self.out)

    def deal_time_msg(self, time):
        if self.time > 0:
            self.time -= 1
            msg = ModuleMsg(ModuleMsg.TIME_MSG_TYPE, [self.time])
        else:
            (x_grid, y_grid) = self.gobang.random_stone(self.color)
            ModuleMsg(ModuleMsg.PUT_MSG_TYPE, self.color, x_grid, y_grid)

            self.time = Gobang.RELAY_TIME
            self.status = "WAIT"

    def send_exit_msg(self):
        ModuleMsg(ModuleMsg.EXIT_MSG_TYPE).send(self.out)

    def deal_exit_msg(self):
        self.is_exit = True
        self.work_thread.join()

    def recv_msg(self, msg):
        if msg.msg_type == ModuleMsg.START_MSG_TYPE:
            self.deal_start_msg()
        elif msg.msg_type == ModuleMsg.PUT_MSG_TYPE:
            self.deal_putdown_msg(self, msg.content[0], msg.content[1])
        elif msg.msg_type == ModuleMsg.TIME_MSG_TYPE:
            self.deal_time_msg(self, msg.content[0])
        elif msg.msg_type == ModuleMsg.EXIT_MSG_TYPE:
            self.deal_exit_msg()


    def work_thread(self):
        inputs = [self.fin]
        outputs = []
        timeout = 1

        print "human thread started"
        self.is_exit = False
        while False == self.is_exit:
            readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
            if readable or writable or exceptional:
                for fd in readable:
                    if fd is self.fin:
                            msg = ModuleMsg().recv(fd)
                            self.recv_msg(msg)
            elif "GO" == self.status:
                self.send_time_msg()
        print "human thread stoped"

    def start(self):
        self.work = Thread(target = self.work_thread)
        self.work.start()
