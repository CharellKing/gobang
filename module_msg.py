#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys

import json

class ModuleMsg(object):
    INVALID_MSG_TYPE = -1
    START_MSG_TYPE = 0
    STOP_MSG_TYPE = 1
    COLOR_MSG_TYPE = 2
    TIME_MSG_TYPE = 3
    PUT_MSG_TYPE = 4
    THREAD_EXIT_MSG_TYPE = 6
    LISTEN_MSG_TYPE = 7
    CONNECT_MSG_TYPE = 8
    EXIT_MSG_TYPE = 9
    LISTEN_SUCC_MSG_TYPE = 10
    LISTEN_ERR_MSG_TYPE = 11

    CONNECT_SUCC_MSG_TYPE = 12
    CONNECT_ERR_MSG_TYPE = 13
    SRV_RECV_CONN_MSG_TYPE = 14

    PROMT_LOG_MSG_TYPE = 100
    PROMT_COLOR_MSG_TYPE = 101
    PROMT_WAIT_MSG_TYPE = 102
    PROMT_GO_MSG_TYPE = 103
    PROMT_TIME_MSG_TYPE = 104
    PROMT_EXIT_MSG_TYPE = 105

    MAX_MSG_LEN = 5120


    def __init__(self, msg_type = INVALID_MSG_TYPE, content = []):
        self.msg_type = msg_type
        self.content = content

    def encode(self):
        return json.dumps([self.msg_type, self.content])

    def decode(self, msg):
        (self.msg_type, self.content) = json.loads(msg)
        return self

    def send(self, out):
        os.write(out, self.encode() + "\n")

    def net_send(self, out):
        out.send(self.encode() + "\n")

    def recv(self, fin):
        line = os.read(fin, ModuleMsg.MAX_MSG_LEN).strip('\n')
        if "" == line:
            self.msg_type = ModuleMsg.INVALID_MSG_TYPE
        else:
            try:
                self.decode(line)
            except:
                print "xxxxxxxxxxxxxxxxx[%s]xxxxxxxxxxxxxxxxxxxx" %(line)
        return self
