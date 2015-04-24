#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys
import re
from threading import Thread
import socket, select

from const_str import ConstStr
from human_role import HumanRole
from robot_role import RobotRole
from net_role import NetRole
from module_msg import ModuleMsg
from gobang import Gobang, Stone

class CmdMsg(object):
    JOIN_MODE = "join_mode"
    START_GAME = "start_game"
    STOP_GAME = "stop_game"
    PUT_DOWN = "put_down"
    HOLD = "hold"
    ATTENT = "attent"
    EXIT_MODE = "exit_mode"
    EXIT = "exit"
    CHESS = "show_chess"
    HELP = "show_help"

    def __init__(self, cmd_msg):
        self.content = cmd_msg.split(" ")


class CmdController(object):
    ROBOTPLAY_MODE = "人机对弈"
    NETPLAY_MODE   = "网络对弈"
    NETWORK_PORT = 8889

    def __init__(self):
        self.nickname = None   #玩家昵称
        self.mode = None      #模式人机对弈与网络对弈

        self.roles = [None, None]

        self.handles = {CmdMsg.JOIN_MODE: self.join_mode_with_promt,
                        CmdMsg.EXIT_MODE: self.exit_mode_with_promt,
                        CmdMsg.HOLD: self.hold_with_promt,
                        CmdMsg.ATTENT: self.attent_with_promt,
                        CmdMsg.START_GAME: self.start_game_with_promt,
                        CmdMsg.STOP_GAME: self.stop_game_with_promt,
                        CmdMsg.PUT_DOWN: self.put_down_with_promt,
                        CmdMsg.EXIT: self.exit_with_promt,
                        CmdMsg.CHESS: self.show_chess,
                        CmdMsg.HELP: self.show_help}

        self.thread_is_exit = True

        self.is_exit = False

        self.interface_in = None
        self.work = None

        self.thread_func = self.work_thread
        self.watch_file = None

    def set_nickname(self, nickname):
        self.nickname = nickname

    def set_thread_func(self, thread_func):
        self.thread_func = thread_func

    def is_starting(self):
        return None != self.roles[0] and True == self.roles[0].is_starting()

    def is_net_running(self):
        return CmdController.NETPLAY_MODE == self.mode and None != self.roles[1] and True == self.roles[1].net_is_running()

    def input_promt(self):
        color_str = ""
        if None != self.roles[0] and None != self.roles[0].color:
            color_str = "黑色" if self.roles[0].color == Stone.BLACK else "白色"

        status = "stop"
        if None != self.roles[0] and None != self.roles[0].status:
            status = self.roles[0].status

        return "%s@%s %s[%s]$" %(str(self.nickname), str(self.mode), color_str, status)

    def input(self, promt):
        return raw_input("%s %s>" %(self.input_promt(), promt)).strip('\n')

    def output_promt(self):
        return "哈喽, %s!" %(str(self.nickname))

    def output(self, promt):
        print "%s %s." %(self.output_promt(), promt)

    def input_nickname(self):
        while None == self.nickname or "" == self.nickname:
            self.nickname = self.input("请输入您的昵称")

        self.output("欢迎进入五子棋的世界")

    def join_mode_with_promt(self, cmd_msg):
        if len(cmd_msg.content) <= 1 or \
          (cmd_msg.content[1] != CmdController.NETPLAY_MODE and \
           cmd_msg.content[1] != ConstStr.ROBOTPLAY_MODE):
            self.output("[join_mode] 后面应该紧跟正确的模式名称[%s|%s]" %(CmdController.NETPLAY_MODE, CmdController.ROBOTPLAY_MODE))
        elif None != self.mode and cmd_msg.content[1] != self.mode:
            if ('y' == self.input("您正处于[%s]模式, 是否要离开(y-yes, n-no)" %(self.mode))):
                self.join_mode_without_promt(cmd_msg)
        else:
            self.join_mode_without_promt(cmd_msg)

    def join_mode_without_promt(self, cmd_msg):
        if cmd_msg.content[1] != self.mode:
            self.mode = cmd_msg.content[1]
            if False == self.thread_is_exit:
                self.roles[0].send_thread_exit_msg()
                self.work.join()

            if CmdController.ROBOTPLAY_MODE == self.mode:
                self.deal_robot_mode()
            else:
                self.deal_net_mode()

    def stop_conn_without_promt(self):
        if CmdController.NETPLAY_MODE == self.mode:
            self.roles[0].send_stop_conn_msg(ModuleMsg(ModuleMsg.STOP_CONN_MSG_TYPE))

    def deal_robot_mode(self):
        robot_in, human_out = os.pipe()
        human_in, robot_out = os.pipe()
        self.interface_in, human_interface_out = os.pipe()

        robot_role = RobotRole(robot_in, robot_out)
        human_role = HumanRole(human_in, human_out, human_interface_out)
        robot_role.start()
        human_role.start()
        self.roles = [human_role, robot_role]

        self.work = Thread(target = self.thread_func)
        self.work.start()



    def deal_net_mode(self):
        net_in, human_out = os.pipe()
        human_in, net_out = os.pipe()
        self.interface_in, human_interface_out = os.pipe()

        net_role = NetRole(net_in, net_out)
        human_role = HumanRole(human_in, human_out, human_interface_out)
        net_role.start()
        human_role.start()
        self.roles = [human_role, net_role]

        self.work = Thread(target = self.thread_func)
        self.work.start()



    def exit_mode_with_promt(self, cmd_msg):
        if None != self.mode:
            if ('y' == self.input("您正处于[%s]模式, 是否要离开(y-yes, n-no)" %(self.mode))):
                self.exit_mode_without_promt(cmd_msg)
        else:
            self.exit_mode_without_promt(cmd_msg)


    def exit_mode_without_promt(self, cmd_msg):
        self.mode = None

        if False == self.thread_is_exit:
            self.roles[0].send_thread_exit_msg()
            self.work.join()
            self.thread_is_exit = True

    def hold_with_promt(self, cmd_msg):
        if True == self.is_starting():
            self.output("游戏正开始中")
        elif CmdController.ROBOTPLAY_MODE == self.mode:
            self.output("您正处于[%s]模式" %(self.mode))
        else:
            if False == self.hold_without_promt(cmd_msg):
                self.output("端口不正确")



    def hold_without_promt(self, cmd_msg):
        if None == self.roles[0] or None == self.roles[1]:
            self.deal_net_mode()

        self.mode = CmdController.NETPLAY_MODE

        port = "%d" %(CmdController.NETWORK_PORT)
        if len(cmd_msg.content) >= 2 and True == CmdController.is_int(cmd_msg.content[1]):
            port = int(cmd_msg.content[1])



        self.roles[0].send_listen_msg(ModuleMsg(ModuleMsg.LISTEN_MSG_TYPE, [port]))


        return True

    def attent_with_promt(self, cmd_msg):
        if True == self.is_starting():
            self.output("游戏正开始中")
        elif CmdController.ROBOTPLAY_MODE == self.mode:
            self.output("您正处于[%s]模式" %(self.mode))
        else:
            if False == self.attent_without_promt(cmd_msg):
                self.output("加入网络对弈失败")


    def attent_without_promt(self, cmd_msg):
        if None == self.roles[0] or None == self.roles[1]:
            self.deal_net_mode()

        self.mode = CmdController.NETPLAY_MODE

        if len(cmd_msg.content) < 2 or \
            False == CmdController.is_ip(cmd_msg.content[1]) or \
            (len(cmd_msg.content) >= 3 and False == CmdController.is_int(cmd_msg.content[2])):
            return False


        host = cmd_msg.content[1]
        port = CmdController.NETWORK_PORT
        if len(cmd_msg.content) >= 3:
            port = int(cmd_msg.content[2])

        self.roles[0].send_conn_msg(ModuleMsg(ModuleMsg.CONNECT_MSG_TYPE, [host, port]))
        return True


    def start_game_with_promt(self, cmd_msg):
        if None == self.mode:
            self.output("您还没有进入任何模式")
        elif CmdController.NETPLAY_MODE == self.mode and False == self.is_net_running():
            self.output("您处于%s模式, 对弈双方网络连接还没有连接起来" %(self.mode))
        elif self.is_starting():
            self.output("您已经在游戏中了")
        else:
            self.start_game_without_promt(cmd_msg)

    def start_game_without_promt(self, cmd_msg):
        self.roles[0].send_start_msg()


    def stop_game_with_promt(self, cmd_msg):
        if True == self.is_starting():
            if "y" == self.input("是否停止游戏(y-是, n-否)"):
                self.stop_game_without_promt(cmd_msg)


    def stop_game_without_promt(self, cmd_msg):
        if True == self.is_starting():
            self.roles[0].send_stop_msg(Gobang.UNKNOWN, Gobang.UNKNOWN)


    @staticmethod
    def is_int(str):
        try:
            int(str)
            return True
        except:
            return False

    @staticmethod
    def is_ip(str):
        values = re.match(r"^(((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(:[1-9]\d*){0,1}).*" , str)
        if None == values:
            return False
        else:
            return True

    def put_down_with_promt(self, cmd_msg):
        if False == self.is_starting():
            self.output("游戏还没开始运行")
        elif len(cmd_msg.content) < 3 or \
            False == CmdController.is_int(cmd_msg.content[1]) or \
            False == CmdController.is_int(cmd_msg.content[2]):
            self.output("[put_down] 后面紧跟行号和列号")
        else:
            self.put_down_without_promt(cmd_msg)


    def put_down_without_promt(self, cmd_msg):
        x_grid = int(cmd_msg.content[1])
        y_grid = int(cmd_msg.content[2])

        if x_grid >= 0 and x_grid < Gobang.GRIDS and \
           y_grid >= 0 and y_grid < Gobang.GRIDS and \
           self.is_starting() and False == self.roles[0].gobang.is_taken_up(x_grid, y_grid) and \
           "GO" == self.roles[0].status:
            self.roles[0].send_putdown_msg(x_grid, y_grid)



    def exit_with_promt(self, cmd_msg):
        if True == self.is_starting() and 'y' == self.input("您正处于运行状态,是否要离开?(y-是, n-否)"):
            self.output("拜拜!")
            self.exit_without_promt(cmd_msg)
        else:
            self.output("拜拜!")
            self.exit_without_promt(cmd_msg)


    def exit_without_promt(self, cmd_msg):
        if False == self.thread_is_exit:
            self.roles[0].send_thread_exit_msg()
            self.thread_is_exit = True
        self.is_exit = True

        if None != self.roles[0] and None != self.roles[0].work:
            self.roles[0].work.join()
        if None != self.roles[1] and None != self.roles[1].work:
            self.roles[1].work.join()
        if None != self.work:
            self.work.join()

    def show_chess(self, cmd_msg):
        if False == self.is_starting():
            self.output("游戏还没开始")
        else:
            chess = self.roles[0].gobang.get_chess()
            for i in xrange (0, Gobang.GRIDS):
                print "%s" %(''.join(chess[i]))

    def show_help(self, cmd_msg):
        print "%s%s%s%s%s%s%s%s%s%s" %("join_mode   进入模式(人机对弈|网络对弈)\n",
                                       "exit_mode   退出模式\n",
                                       "hold        主持游戏(端口)\n",
                                       "attend      参加游戏(ip, 端口)\n",
                                       "start_game  开始游戏\n",
                                       "stop_game   停止游戏\n",
                                       "show_chess  显示棋局\n",
                                       "put_down    落子(row, col)\n",
                                       "exit        退出游戏\n",
                                       "help        帮助\n")

    def interact(self):
        while(False == self.is_exit):
            line = self.input("")
            if "" == line:
                continue

            cmd_msg = CmdMsg(line)
            if False == self.handles.has_key(cmd_msg.content[0]):
                self.output("无效的命令")
            else:
                self.handles[cmd_msg.content[0]](cmd_msg)


    def recv_msg(self, msg):
        if msg.msg_type == ModuleMsg.PROMT_LOG_MSG_TYPE:
            self.watch_file.write(msg.content[0] + "\r\n")
            self.watch_file.flush()
        elif msg.msg_type == ModuleMsg.THREAD_EXIT_MSG_TYPE:
            self.watch_file.write("cmd recv thread exit msg" + "\r\n")
            self.watch_file.flush()
            self.thread_is_exit = True
        elif msg.LISTEN_SUCC_MSG_TYPE == msg.msg_type:
            self.watch_file.write("cmd recv listen success" + "\r\n")
            self.watch_file.flush()
        elif msg.LISTEN_ERR_MSG_TYPE == msg.msg_type:
            self.watch_file.write("cmd recv listen error:%s" %(msg.content[0].replace('huanhang', '\n')) + "\r\n")
            self.watch_file.flush()
        elif msg.CONNECT_SUCC_MSG_TYPE == msg.msg_type:
            self.watch_file.write("cmd recv connect success" + "\r\n")
            self.watch_file.flush()
        elif msg.CONNECT_ERR_MSG_TYPE == msg.msg_type:
            self.watch_file.write("cmd recv connect error:%s" %(msg.content[0].replace('huanhang', '\n')) + "\r\n")
            self.watch_file.flush()
        elif msg.SRV_RECV_CONN_MSG_TYPE == msg.msg_type:
            self.watch_file.write("cmd recv %s connect me" %(msg.content[0]) + "\r\n")
            self.watch_file.flush()
        elif msg.msg_type == ModuleMsg.EXIT_MSG_TYPE:
            self.watch_file.write("cmd recv exit msg" + "\r\n")
            self.watch_file.flush()
            self.thread_is_exit = True
            self.is_exit = True

    def work_thread(self):
        inputs = [self.interface_in]
        outputs = []
        timeout = 1
        self.thread_is_exit = False
        self.watch_file.truncate()
        self.watch_file.flush()
        while False == self.thread_is_exit:
            readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
            if readable or writable or exceptional:
                for fd in readable:
                    if fd is self.interface_in:
                        msg_strs = os.read(fd, ModuleMsg.MAX_MSG_LEN).split('\n')
                        for msg_str in msg_strs:
                            if "" != msg_str:
                                msg = ModuleMsg().decode(msg_str)
                                self.recv_msg(msg)


        for role in self.roles:
            role.work.join()

        self.roles = [None, None]



    def run(self):
        self.input_nickname()
        self.watch_file = open("watch_%d_%s.log" %(os.getpid(), self.nickname), 'w')
        self.is_exit = False
        self.interact()
        self.thread_is_exit = True
        if self.work:
            self.work.join()
        self.watch_file.close()
