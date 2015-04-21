#!/usr/bin/python
#-*-coding:utf-8-*-

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
        self.is_exit = True
        self.color = None
        self.status = None
        self.time = None
        self.gobang = None


    def deal_start_msg(self):
        self.color = Gobang.random_order()
        self.gobang = Gobang()
        msg = ModuleMsg(ModuleMsg.COLOR_MSG_TYPE, [not self.color]).send(self.out)
        if self.color == Stone.WHITE:
            self.status = "GO"
            self.deal_putdown_msg(None, None)
        else:
            self.status = "WAIT"
        self.time = Gobang.RELAY_TIME

    def deal_putdown_msg(self, x_grid, y_grid):
        (put_x_grid, put_y_grid) = (Gobang.GRIDS >> 1, Gobang.GRIDS >> 1)
        if None == x_grid and None == y_grid:
            self.gobang.put_stone(x_grid, y_grid)
        else:
            (x_grid, y_grid) = self.gobang.random_order(self.color)
        self.status = "WAIT"
        msg = ModuleMsg(ModuleMsg.PUT_MSG_TYPE, self.color, x_grid, y_grid).send(self.out)


    def deal_time_msg(self, time):
        self.time = time

    def deal_exit_msg(self):
        self.is_exit = True

    def recv_msg(self, msg):
        if msg.msg_type == ModuleMsg.START_MSG_TYPE:
            self.deal_start_msg()
        elif msg.msg_type == ModuleMsg.PUT_MSG_TYPE:
            self.deal_putdown_msg(self, msg.content[0], msg.content[1])
        elif msg.msg_type == ModuleMsg.TIME_MSG_TYPE:
            self.deal_time_msg(self, msg.content[0])
        elif msg.msg_type == ModuleMsg.EXIT_MSG_TYPE:
            self.deal_exit_msg()

    def time_out(self, msg):
        if self.time > 0:
            self.time -= 1
            msg = ModuleMsg(ModuleMsg.TIME_MSG_TYPE, [self.time])
        else:
            self.time = Gobang.RELAY_TIME
            (x_grid, y_grid) = self.gobang.RandomStone(self.color)
            ModuleMsg(ModuleMsg.PUT_MSG_TYPE, self.color, x_grid, y_grid)
            self.status = "WAIT"

    def work_thread(self):
        inputs = [self.fin]
        outputs = []
        timeout = 1

        print "robot thread started"
        self.is_exit = False
        while False == self.is_exit:
            readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
            if readable or writable or exceptional:
                for fd in readable:
                    if fd is self.fin:
                        msg = ModuleMsg().recv(fd)
                        self.recv_msg(msg)
            elif "GO" == self.status:
                self.time_out(msg)
        print "robot thread stop"

    def start(self):
        self.work = Thread(target = self.work_thread)
        self.work.start()
