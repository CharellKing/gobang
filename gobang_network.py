#!/usr/bin/python

import socket, select
from threading import Thread
import Queue
import wx

class GobangServer(object):
    def __init__(self, host, port, gui):
        self.host = host
        self.port = int(port)
        self.inputs = []
        self.outputs = []
        self.message_queues = {}
        self.gui = gui


    def WorkerThread(self, args):
        (svr_sock) = args
        self.inputs = [svr_sock]
        self.outputs = []
        timeout = None

        while self.inputs:
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs, timeout)

            if not (readable or writable or exceptional):
                print "timeout"
                break
            else:
                for sock in readable:
                    if sock is svr_sock:
                        timeout = 5
                        conn, client_address = sock.accept()
                        print client_address
                        wx.CallAfter(self.gui.status_static.SetLabel, "%s connected" %(client_address[0]))
                        # self.gui.status_static.SetLabel("%s connected" %(client_address[0]))
                        conn.setblocking(0)
                        self.inputs.append(conn)
                        self.message_queues[conn] = Queue.Queue()
                        # conn.send()
                    else:
                        data = sock.recv(1024)
                        if data:
                            self.message_queues[sock].put(data)
                            if sock not in self.outputs:
                                self.outputs.append(sock)
                            else:
                                if sock in self.outputs:
                                    self.outputs.remove(sock)
                                    self.inputs.remove(sock)
                                    sock.close()
                                    del message_queues[sock]

        for sock in exceptional:
            inputs.remove(sock)
            if sock in outputs:
                outputs.remove(sock)
            sock.close()
            del message_queues[sock]


    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)

        worker = Thread(target = self.WorkerThread, args = (self.sock,))
        worker.start()

class GobangClient(object):
    def __init__(self, host, port, gui):
        self.host = host
        self.port = int(port)
        self.sock = None
        self.conn = None
        self.inputs = []
        self.outputs = []
        self.gui = gui

    def WorkerThread(self, args):
        (cli_sock) = args
        self.inputs = [cli_sock]
        self.outputs = [cli_sock]
        timeout = 5
        print type(cli_sock)
        while self.inputs:
            readable, writable, exceptional = select.select([], self.outputs, self.inputs, timeout)

            if not (readable or writable or exceptional):
                print "timeout"
                break
            else:
                for sock in readable:
                    data = sock.recv(1024)
                    if data:
                        self.message_queues[sock].put(data)
                        if sock not in outputs:
                            outputs.append(sock)
                        else:
                            if sock in outputs:
                                outputs.remove(sock)
                                inputs.remove(sock)
                                sock.close()
                                del message_queues[sock]

        for sock in exceptional:
            inputs.remove(sock)
            if sock in outputs:
                outputs.remove(sock)
            sock.close()
            del message_queues[sock]

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        worker = Thread(target = self.WorkerThread, args = (self.sock, ))
        worker.start()
