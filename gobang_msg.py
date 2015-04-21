#!/usr/bin/python

import json

class GobangMsg(object):
    START_MSG_TYPE = 0
    TRUN_MSG_TYPE = 1
    TIME_MSG_TYPE = 2
    PUT_MSG_TYPE = 3


    def __init__(self, type = 0, content = []):
        self.type = type
        self.content = content

    def encode(self):
        return json.dumps([self.type, self.content])

    def decode(self, msg):
        (self.type, self.content) = json.loads(msg)
