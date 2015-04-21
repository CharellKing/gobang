#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys

import socket, select
from threading import Thread
from gobang_msg import GobangMsg


class GobangServer(object):
    def __init__(self, host, port, net_in, net_out):
        self.host = host
        self.port = int(port)
        self.svr_sock = None
        self.conn_sock = None

        self.work_thread = None
        self.is_exit = False


    def work_thread(self):
        inputs = [net_in, self.svr_sock]
        outputs = []
        timeout = None

        while inputs and False == self.is_exit:
            readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
            if readable or writable or exceptional:
                for fd in readable:
                    if fd is self.svr_sock:
                        timeout = 1
                        self.conn_sock, client_address = sock.accept()
                        self.conn.setblocking(0)
                        inputs.append(self.conn)

                    elif fd is self.conn_sock:
                        print "conn"
                    elif fd is self.net_in:
                        print "net"


    def start(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.host, self.port))
            self.sock.listen(1)
            self.is_start = True
            self.work_thread = Thread(target = self.work_thread)
            self.work_thread.start()
            return True
        except Exception, ex:
            self.gui.status_static.SetLabel("listen failed!!!!!")
            print Exception, ":", ex
            return False


    def stop(self):
        self.is_start = False
        self.work_thread.join()
        if None != self.conn:
            self.conn.close()
            self.conn = None
        if None != self.sock:
            self.sock.close()
            self.sock = None

    def send(self, msg):
        if None != self.conn:
            self.conn.send(msg.encode() + '###')


class GobangClient(object):
    def __init__(self, host, port, net_in, net_out):
        self.host = host
        self.port = int(port)
        self.conn_sock = None

        self.net_in = net_in
        self.net_out = net_out
        self.is_exit = False

    def work_thread(self):
        inputs = [self.conn_sock, self.net_in]
        outputs = []
        while False == self.is_exit:
            readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
            if (readable or writable or exceptional):
                for fd in readable:
                    if fd is self.conn_sock:
                        print "conn"
                    elif fd is self.net_in:
                        print "net"


    def start(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.is_start = True
            worker = Thread(target = self.work_thread)
            worker.start()
            return True
        except Exception, ex:
            print Exception, ":", ex
            return False


    def stop(self):
        self.is_exit = True

        self.work_thread.join()
        if self.sock:
            self.sock.close()
            self.sock = None
        if self.conn:
            self.conn.close()
            self.conn = None

    def send(self, msg):
        self.sock.send(msg.encode())
