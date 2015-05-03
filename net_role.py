#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys
import traceback
import time

from threading import Thread
import socket, select

from gobang import Gobang
from human_role import HumanRole
from robot_role import RobotRole
from module_msg import ModuleMsg


class NetRole(object):
    def __init__(self, net_in,  net_out):
        self.inputs = []
        self.fin = net_in
        self.out = net_out

        self.svr_sock = None
        self.cli_conn = None

        self.thread_is_exit = True

        self.work = None


    # 判断网络是否启动
    def net_is_running(self):
        return (None == self.svr_sock and None != self.cli_conn) or \
          (None != self.svr_sock and None != self.cli_conn)


    #处理来自human_role的监听消息
    def recv_listen_from_human(self, msg):
        try:
            port = msg.content[0]
            # self.svr_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            # self.svr_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            self.svr_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.svr_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.svr_sock.bind(("127.0.0.1", int(port)))
            self.svr_sock.listen(1)
            self.inputs.append(self.svr_sock)
            ModuleMsg(ModuleMsg.LISTEN_SUCC_MSG_TYPE).send(self.out)
        except:
            print sys.exc_info()[0],sys.exc_info()[1]
            if self.svr_sock:
                self.svr_sock.close()
                self.svr_sock = None
            ModuleMsg(ModuleMsg.LISTEN_ERR_MSG_TYPE, ["%s %s" %(sys.exc_info()[0],sys.exc_info()[1])]).send(self.out)


    # 处理来自human_role的连接消息
    def recv_conn_from_human(self, msg):
        try:
            # socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            (host, port) = msg.content
            self.cli_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cli_conn.connect((host, int(port)))
            self.inputs.append(self.cli_conn)
            ModuleMsg(ModuleMsg.CONNECT_SUCC_MSG_TYPE).send(self.out)
        except:
            print sys.exc_info()[0],sys.exc_info()[1]
            if self.cli_conn:
                self.cli_conn.close()
                self.cli_conn = None

            ModuleMsg(ModuleMsg.CONNECT_ERR_MSG_TYPE, ["%s %s" %(sys.exc_info()[0],sys.exc_info()[1])]).send(self.out)



    #处理来自human_role的线程退出消息
    def recv_thread_exit_from_human(self, msg):
        if None != self.cli_conn:
            msg.net_send(self.cli_conn)
        self.thread_is_exit = True

    #处理来自human_role的停止消息
    def recv_stop_from_human(self, msg):
        if None != self.cli_conn:
            msg.net_send(self.cli_conn)
        self.stop_sock()

    #处理来自human_role的游戏退出消息
    def recv_exit_from_human(self, msg):
        if None != self.cli_conn:
            msg.net_send(self.cli_conn)
        self.thread_is_exit = True


    #处理来自human_role的消息
    def recv_msg_from_human(self, msg):
        if msg.msg_type == ModuleMsg.LISTEN_MSG_TYPE:
            self.recv_listen_from_human(msg)
        elif msg.msg_type == ModuleMsg.CONNECT_MSG_TYPE:
            self.recv_conn_from_human(msg)
        elif msg.msg_type == ModuleMsg.THREAD_EXIT_MSG_TYPE:
            self.recv_exit_from_human(msg)
        elif msg.msg_type == ModuleMsg.INVALID_MSG_TYPE:
            return
        elif msg.msg_type == ModuleMsg.EXIT_MSG_TYPE:
            self.recv_exit_from_human(msg)
        elif msg.msg_type == ModuleMsg.STOP_MSG_TYPE:
            self.recv_stop_from_human(msg)
        else:
            if None != self.cli_conn:
                msg.net_send(self.cli_conn)

    #关闭套接字
    def stop_sock(self):
        if None != self.cli_conn:
            self.inputs.remove(self.cli_conn)
            self.cli_conn.shutdown(socket.SHUT_RDWR)
            self.cli_conn.close()
            self.cli_conn = None

        if None != self.svr_sock:
            self.inputs.remove(self.svr_sock)
            self.svr_sock.shutdown(socket.SHUT_RDWR)
            self.svr_sock.close()
            self.svr_sock = None

    #接收来自网络的退出游戏的消息
    def recv_exit_from_sock(self, msg):
        ModuleMsg(ModuleMsg.STOP_MSG_TYPE, [Gobang.UNKNOWN, None, None, None]).send(self.out)
        self.stop_sock()

    #接收来自网络的线程退出的消息
    def recv_thread_exit_from_sock(self, msg):
        msg.send(self.out)
        self.thread_is_exit = True

    #接收来自网络的停止游戏的消息
    def recv_stop_from_sock(self, msg):
        msg.send(self.out)
        self.stop_sock()

    #处理接收来自网路的消息
    def recv_msg_from_sock(self, msg):
        if ModuleMsg.EXIT_MSG_TYPE == msg.msg_type:
            self.recv_exit_from_sock(msg)
        elif ModuleMsg.THREAD_EXIT_MSG_TYPE == msg.msg_type:
            self.recv_thread_exit_from_sock(msg)
        elif ModuleMsg.STOP_MSG_TYPE == msg.msg_type:
            self.recv_stop_from_sock(msg)
        elif ModuleMsg.INVALID_MSG_TYPE != msg.msg_type:
            msg.send(self.out)


    #net_role的工作线程
    def work_thread(self):
        self.inputs = [self.fin]
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
                                self.recv_msg_from_human(msg)
                    elif fd is self.svr_sock:
                        (self.cli_conn, addr) = self.svr_sock.accept()
                        self.inputs.append(self.cli_conn)
                        ModuleMsg(ModuleMsg.SRV_RECV_CONN_MSG_TYPE, [addr]).send(self.out)
                    elif fd is self.cli_conn:
                        msg_strs = fd.recv(ModuleMsg.MAX_MSG_LEN).split('\n')
                        for msg_str in msg_strs:
                            if "" != msg_str:
                                msg = ModuleMsg().decode(msg_str)
                                self.recv_msg_from_sock(msg)

                for fd in exceptional:
                    self.thread_is_exit = True
                    ModuleMsg(ModuleMsg.THREAD_EXIT_MSG_TYPE).send(self.out)

        self.inputs.remove(self.fin)
        os.close(self.fin)
        os.close(self.out)

        if self.cli_conn:
           self.cli_conn.close()
           self.cli_conn = None

        if self.svr_sock:
            self.svr_sock.close()
            self.svr_sock = None


    #开始net_role模块，主要是开启net_role的线程
    def start(self):
        self.work = Thread(target = self.work_thread)
        self.work.start()
