#!/usr/bin/python
#-*-coding:utf-8-*-

class RobotRole(object):
    def __init__(self, robot_in, robot_out):
        self.robot_in = robot_in
        self.robot_out = robot_out
        self.timeout = None

        self.is_running = False


    def deal_msg(self, msg):
        if msg.type == GobangMsg.START_MSG_TYPE:
            msg = GobangMsg(GobangMsg.START_MSG_TYPE)
            self.robot_out.write(msg.encode())
            self.timeout = 1


    def work_thread(self):
        inputs = [self.robot_in]
        outputs = []
        timeout = None

        while self.is_running:
            readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
            if readable or writable or exceptional:
                for rin in readable:
                    data = rin.readline().strip('\n')
                    msg = GobangMsg()
                    msg.decode(data)
                    self.deal_msg(msg)

    def run(self):
        self.is_running = True
        worker = Thread(target = self.worker_thread, args = ())
