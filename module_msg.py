#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys

import json

class ModuleMsg(object):
    INVALID_MSG_TYPE = -1     #无效的消息类型
    START_MSG_TYPE = 0        #开始游戏的消息类型
    STOP_MSG_TYPE = 1         #停止游戏的消息类型
    COLOR_MSG_TYPE = 2        #所持棋子的颜色类型
    TIME_MSG_TYPE = 3         #计时的消息类型
    PUT_MSG_TYPE = 4          #落子
    THREAD_EXIT_MSG_TYPE = 6  #线程退出
    LISTEN_MSG_TYPE = 7       #监听
    CONNECT_MSG_TYPE = 8      #连接
    EXIT_MSG_TYPE = 9         #退出游戏
    LISTEN_SUCC_MSG_TYPE = 10 #监听成功
    LISTEN_ERR_MSG_TYPE = 11  #监听失败

    CONNECT_SUCC_MSG_TYPE = 12#连接成功
    CONNECT_ERR_MSG_TYPE = 13 #连接失败
    SRV_RECV_CONN_MSG_TYPE = 14 #服务器接收客户端的连接消息

    PROMT_LOG_MSG_TYPE = 100   #cmd、gui日志
    PROMT_COLOR_MSG_TYPE = 101 #cmd、gui颜色
    PROMT_WAIT_MSG_TYPE = 102  #等待
    PROMT_GO_MSG_TYPE = 103    #运行
    PROMT_TIME_MSG_TYPE = 104  #计时
    PROMT_EXIT_MSG_TYPE = 105  #退出

    MAX_MSG_LEN = 5120         #消息缓冲区最大长度


    def __init__(self, msg_type = INVALID_MSG_TYPE, content = []):
        self.msg_type = msg_type
        self.content = content

    def encode(self):
        return json.dumps([self.msg_type, self.content])

    def decode(self, msg):
        (self.msg_type, self.content) = json.loads(msg)
        return self

    #管道消息发送
    def send(self, out):
        os.write(out, self.encode() + "\n")

    #网络消息发送
    def net_send(self, out):
        out.send(self.encode() + "\n")

    #接收消息，将json转化到各个type、contents
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
