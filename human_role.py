#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys
from threading import Thread
import socket, select

from module_msg import ModuleMsg
from gobang import Gobang, Stone

class HumanRole(object):
    def __init__(self, human_in, human_out, human_interface_in, human_interface_out):
        self.inputs = []
        self.fin= human_in
        self.out = human_out
        self.interface_in = human_interface_in
        self.interface_out = human_interface_out

        self.timeout = None

        self.work = None
        self.thread_is_exit = True
        self.color = None
        self.status = None
        self.time = Gobang.RELAY_TIME
        self.gobang = None

        self.is_start = False

    def is_starting(self):
        return None != self.status and True == self.is_start

    def send_color_msg(self):
        ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human send color msg"]).send(self.interface_out)

        self.time = Gobang.RELAY_TIME
        self.color = Gobang.random_order()
        self.gobang = Gobang()
        print "send %d" %(self.color)
        ModuleMsg(ModuleMsg.COLOR_MSG_TYPE, [not self.color]).send(self.out)
        if self.color == Stone.WHITE:
            self.status = "GO"
        else:
            self.status = "WAIT"



    def recv_color_msg(self, msg):
        ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human recv color msg"]).send(self.interface_out)
        color = msg.content[0]
        self.is_start = True
        self.color = color
        print "recv %d" %(self.color)
        if Stone.WHITE == color:
            self.status = "GO"
            print "human go"
        else:
            self.status = "WAIT"
            print "human wait"

    def send_start_msg(self, msg):
        ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human send start msg"]).send(self.interface_out)

        self.gobang = Gobang()
        self.is_start = True
        msg.send(self.out)

    def recv_start_msg(self, msg):
        ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human recv start_msg"]).send(self.interface_out)

        if True == self.is_start:
            self.send_color_msg()


    def send_stop_msg(self, msg):
        print "send_stop_msg"
        self.is_start = False
        self.status = None
        self.time = Gobang.RELAY_TIME

        (self_ret, x_grid, y_grid, color) = msg.content
        if Gobang.UNKNOWN == self_ret:
            competitor_ret = Gobang.UNKNOWN
        else:
            competitor_ret = -self_ret

        ModuleMsg(ModuleMsg.STOP_MSG_TYPE, [competitor_ret, x_grid, y_grid, color]).send(self.out)

        ModuleMsg(ModuleMsg.STOP_MSG_TYPE, [self_ret, x_grid, y_grid, color]).send(self.interface_out)



    def recv_stop_msg(self, msg):
        (ret, x_grid, y_grid, color) = msg.content
        if None != x_grid and None != y_grid:
            self.gobang.put_stone(x_grid, y_grid, color)
        msg.send(self.interface_out)
        self.is_start = False
        self.status = None
        self.time = Gobang.RELAY_TIME


    def send_putdown_msg(self, msg):
        (x_grid, y_grid, color) = msg.content
        self.time = Gobang.RELAY_TIME
        self.status = "WAIT"
        self.gobang.put_stone(x_grid, y_grid, color)

        if Gobang.UNKNOWN == self.justy_result(x_grid, y_grid):
            msg.send(self.out)
            msg.send(self.interface_out)


    def justy_result(self, x_grid, y_grid):
        self_ret = Gobang.UNKNOWN
        if True == self.gobang.is_tie(x_grid, y_grid):
            self_ret = Gobang.TIED
        if True == self.gobang.is_five(x_grid, y_grid):
            self_ret = Gobang.SUCCESS

        if Gobang.UNKNOWN != self_ret:
            msg = ModuleMsg(ModuleMsg.STOP_MSG_TYPE, [self_ret, x_grid, y_grid, self.color])
            self.send_stop_msg(msg)
        return self_ret

    def recv_putdown_msg(self, msg):
        (x_grid, y_grid, color) = msg.content
        self.gobang.put_stone(x_grid, y_grid, color)
        msg.send(self.interface_out)

        self.status = "GO"
        self.time = Gobang.RELAY_TIME

    def send_time_msg(self):
        if self.time > 0:
            ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["human: send time msg"]).send(self.interface_out)
            self.time -= 1
            msg = ModuleMsg(ModuleMsg.TIME_MSG_TYPE, [self.time])
            msg.send(self.interface_out)
            msg.send(self.out)
        else:
            self.status = "WAIT"
            self.time = Gobang.RELAY_TIME

            (x_grid, y_grid) = self.gobang.random_stone(self.color)

            if Gobang.UNKNOWN == self.justy_result(x_grid, y_grid):
                msg = ModuleMsg(ModuleMsg.PUT_MSG_TYPE, [x_grid, y_grid, self.color])
                msg.send(self.interface_out)
                msg.send(self.out)


    def recv_time_msg(self, msg):
        time = msg.content[0]
        msg.send(self.interface_out)
        self.time = time


    def send_thread_exit_msg(self, msg):
        self.thread_is_exit = True
        msg.send(self.out)
        msg.send(self.interface_out)
        self.time = Gobang.RELAY_TIME

        self.is_start = False
        self.color = None



    def recv_thread_exit_msg(self, msg):
        self.thread_is_exit = True
        self.is_start = False
        msg.send(self.interface_out)
        self.time = Gobang.RELAY_TIME
        self.color = None



    def send_exit_msg(self, msg):
        msg.send(self.out)
        msg.send(self.interface_out)

        self.thread_is_exit = True
        self.is_start = False



    def recv_exit_msg(self, msg):
        ModuleMsg(ModuleMsg.EXIT_MSG_TYPE, [msg.content[0]]).send(self.interface_out)

        self.thread_is_exit = True
        self.is_start = False



    def send_listen_msg(self, msg):
        msg.send(self.out)

    def send_conn_msg(self, msg):
        msg.send(self.out)

    def recv_msg(self, msg):
        if msg.msg_type == ModuleMsg.START_MSG_TYPE:
            self.recv_start_msg(msg)
        elif msg.msg_type == ModuleMsg.COLOR_MSG_TYPE:
            self.recv_color_msg(msg)
        elif msg.msg_type == ModuleMsg.PUT_MSG_TYPE:
            self.recv_putdown_msg(msg)
        elif msg.msg_type == ModuleMsg.TIME_MSG_TYPE:
            self.recv_time_msg(msg)
        elif msg.msg_type == ModuleMsg.THREAD_EXIT_MSG_TYPE:
            self.recv_thread_exit_msg(msg)
        elif msg.msg_type == ModuleMsg.STOP_MSG_TYPE:
            self.recv_stop_msg(msg)
        elif msg.msg_type == ModuleMsg.EXIT_MSG_TYPE:
            self.recv_exit_msg()
        elif msg.msg_type == ModuleMsg.LISTEN_ERR_MSG_TYPE or  \
          msg.msg_type == ModuleMsg.LISTEN_SUCC_MSG_TYPE or \
          msg.msg_type == ModuleMsg.CONNECT_SUCC_MSG_TYPE or \
          msg.msg_type == ModuleMsg.SRV_RECV_CONN_MSG_TYPE or \
          msg.msg_type == ModuleMsg.CONNECT_ERR_MSG_TYPE:
            msg.send(self.interface_out)
        else:
            ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["[%d]无效的消息" %(msg.msg_type)]).send(self.interface_out)

    def recv_msg_from_interface(self, msg):
        if msg.msg_type == ModuleMsg.LISTEN_MSG_TYPE:
            self.send_listen_msg(msg)
        elif msg.msg_type == ModuleMsg.CONNECT_MSG_TYPE:
            print "send_conn_msg"
            self.send_conn_msg(msg)
        elif msg.msg_type == ModuleMsg.START_MSG_TYPE:
            self.send_start_msg(msg)
        elif msg.msg_type == ModuleMsg.PUT_MSG_TYPE:
            self.send_putdown_msg(msg)
        elif msg.msg_type == ModuleMsg.STOP_MSG_TYPE:
            self.send_stop_msg(msg)
        elif msg.msg_type == ModuleMsg.THREAD_EXIT_MSG_TYPE:
            self.send_thread_exit_msg(msg)
        elif msg.msg_type == ModuleMsg.EXIT_MSG_TYPE:
            self.send_exit_msg(msg)
        else:
            ModuleMsg(ModuleMsg.PROMT_LOG_MSG_TYPE, ["[%d]无效的消息" %(msg.msg_type)]).send(self.interface_out)


    def work_thread(self):
        self.inputs = [self.fin, self.interface_in]
        outputs = []
        timeout = 1

        self.thread_is_exit = False
        while False == self.thread_is_exit:
            readable, writable, exceptional = select.select(self.inputs, outputs, self.inputs, timeout)
            if readable or writable or exceptional:
                for fd in readable:
                    if fd is self.fin:
                        msg_strs = os.read(fd, ModuleMsg.MAX_MSG_LEN).split('\n')
                        for msg_str in msg_strs:
                            if "" != msg_str:
                                msg = ModuleMsg().decode(msg_str)
                                self.recv_msg(msg)
                    elif fd is self.interface_in:
                        msg_strs = os.read(fd, ModuleMsg.MAX_MSG_LEN).split('\n')
                        for msg_str in msg_strs:
                            if "" != msg_str:
                                msg = ModuleMsg().decode(msg_str)
                                self.recv_msg_from_interface(msg)


            elif "GO" == self.status and False == self.thread_is_exit:
                self.send_time_msg()

        self.inputs.remove(self.fin)
        self.inputs.remove(self.interface_in)
        os.close(self.fin)
        os.close(self.interface_in)
        os.close(self.out)
        os.close(self.interface_out)
        print "human stop\n"

    def start(self):
        self.work = Thread(target = self.work_thread)
        self.work.start()
