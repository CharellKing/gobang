#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys

from network_service import GobangServer, GobangClient

class NetRole(object):
    def __init__(self, net_in,  net_out):
        self.in = net_in
        self.out = net_out

        self.net_service = None
        self.is_exit = True

    def start_service(host, port, is_hold):
        self.is_exit = True
        if True == is_hold:
            self.network_service = GobangServer(host, port, net_in, net_out)
            if False == self.network_service.start():
                self.network_service = None
                return False
        else:
            self.network_service = GobangClient(host, port, net_in, net_out)
            if False == self.network_service.start():
                self.network_service = None
                return False
        self.is_exit = False
        return True


    def deal_msg(self, msg):
        if msg.type == GobangMsg.START_MSG_TYPE:
            msg = GobangMsg(GobangMsg.START_MSG_TYPE)
            self.robot_out.write(msg.encode())
            self.timeout = 1
