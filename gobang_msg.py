#!/usr/bin/python

import json

class GobangMsg(object):
    START_MSG_TYPE = 0
    START_GAME_MSG_TYPE = 1
    TURN_ON_OTHER = 2
    TIMEOUT_MSG_TYPE = 3
    TIMER_MSG_TYPE = 4
    PUT_MSG_TYPE = 5
    RESULT_MSG_TYPE = 6

    def __init__(self, type = 0, content = []):
        self.type = type
        self.content = content

    def encode(self):
        return json.dumps([self.type, self.content])

    def decode(self, msg):
        (self.type, self.content) = json.loads(msg)
