#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys

import json

class ModuleMsg(object):
    INVALID_MSG_TYPE = -1
    START_MSG_TYPE = 0
    COLOR_MSG_TYPE = 1
    TIME_MSG_TYPE = 3
    PUT_MSG_TYPE = 4
    PROMT_MSG_TYPE = 5
    EXIT_MSG_TYPE = 6


    PROMT_LOG_MSG_TYPE = 10
    PROMT_COLOR_MSG_TYPE = 11
    PROMT_WAIT_MSG_TYPE = 12
    PROMT_GO_MSG_TYPE = 13
    PROMT_TIME_MSG_TYPE = 14
    PROMT_EXIT_MSG_TYPE = 15

    MAX_MSG_LEN = 256


    def __init__(self, msg_type = INVALID_MSG_TYPE, content = []):
        self.msg_type = msg_type
        self.content = content

    def encode(self):
        return json.dumps([self.msg_type, self.content])

    def decode(self, msg):
        (self.msg_type, self.content) = json.loads(msg)

    def send(self, out):
        os.write(out, self.encode() + "\n")

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
