#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys
import re
from threading import Thread

from const_str import ConstStr
from human_role import HumanRole
from robot_role import RobotRole
from network_service import GobangServer, GobangClient
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
        self.contents = cmd_msg.split(" ")


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

        self.is_network_running = False #是否网络运行正常
        self.is_starting = False   #是否正在游戏
        self.is_exit = False

        self.interface_in = None
        self.work = None


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
        if len(cmd_msg.contents) <= 1 or \
          (cmd_msg.contents[1] != CmdController.NETPLAY_MODE and \
           cmd_msg.contents[1] != ConstStr.ROBOTPLAY_MODE):
            self.output("[join_mode] 后面应该紧跟正确的模式名称[%s|%s]" %(CmdController.NETPLAY_MODE, CmdController.ROBOTPLAY_MODE))
        elif None != self.mode and cmd_msg.contents[1] != self.mode:
            if ('y' == self.input("您正处于[%s]模式, 是否要离开(y-yes, n-no)" %(self.mode))):
                self.join_mode_without_promt(cmd_msg)
        else:
            self.join_mode_without_promt(cmd_msg)

    def join_mode_without_promt(self, cmd_msg):
        if cmd_msg.contents[1] != self.mode:
            self.is_starting = False
            if self.mode == CmdController.NETPLAY_MODE:
                self.is_running = False

            self.mode = cmd_msg.contents[1]

            if CmdController.ROBOTPLAY_MODE == self.mode:
                self.deal_robot_mode()
            else:
                self.deal_net_mode()


    def deal_robot_mode(self):
        robot_in, human_out = os.pipe()
        human_in, robot_out = os.pipe()
        self.interface_in, human_interface_out = os.pipe()

        robot_role = RobotRole(robot_in, robot_out)
        human_role = HumanRole(human_in, human_out, human_interface_out)
        robot_role.start()
        human_role.start()
        self.roles = [human_role, robot_role]
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

        self.work.start()



    def exit_mode_with_promt(self, cmd_msg):
        if None != self.mode:
            if ('y' == self.input("您正处于[%s]模式, 是否要离开(y-yes, n-no)" %(self.mode))):
                self.exit_mode_without_promt(cmd_msg)
        else:
            self.exit_mode_without_promt(cmd_msg)


    def exit_mode_without_promt(self, cmd_msg):
        self.is_starting = False
        self.mode = None

    def hold_with_promt(self, cmd_msg):
        if True == self.is_starting:
            self.output("游戏正开始中")
        elif CmdController.ROBOTPLAY_MODE == self.mode:
            self.output("您正处于[%s]模式" %(self.mode))
        else:
            if False == self.hold_without_promt(cmd_msg):
                self.output("主持网络对弈失败")
            else:
                self.output("主持网络对弈成功")


    def hold_without_promt(self, cmd_msg):
        self.mode = CmdController.NETPLAY_MODE

        port = CmdController.NETWORK_PORT
        if len(cmd_msg.contents) >= 2 and False == CmdController.is_int(cmd_msg.contents[1]):
            return False
        else:
            port = int(cmd_msg.contents[1])

        net_service = GobangServer()
        if False == net_service.start():
            return False

        roles[2].set_service(net_service)
        roles[2].start_service()

        self.is_network_running = True
        return True

    def attent_with_promt(self, cmd_msg):
        if True == self.is_starting:
            self.output("游戏正开始中")
        elif CmdController.ROBOTPLAY_MODE == self.mode:
            self.output("您正处于[%s]模式" %(self.mode))
        else:
            if False == self.attent_without_promt(cmd_msg):
                self.output("加入网络对弈失败")
            else:
                self.output("加入网络对弈成功")

    def attent_without_promt(self, cmd_msg):
        self.mode = CmdController.NETPLAY_MODE

        if len(cmd_msg.contents) < 2 or \
            False == CmdController.is_ip(cmd_msg.contents[1]) or \
            (len(cmd_msg.contents) >= 3 and False == CmdController.is_int(cmd_msg.contents[2])):
            return False


        host = cmd_msg.contents[1]
        port = CmdController.NETWORK_PORT
        if len(cmd_msg.contents) >= 3:
            port = int(cmd_msg.contents[2])

        self.is_network_running = True
        return True


    def start_game_with_promt(self, cmd_msg):
        if None == self.mode:
            self.output("您还没有进入任何模式")
        elif CmdController.NETPLAY_MODE == self.mode and False == self.is_network_running:
            self.output("您处于%s模式, 还没有发起或者参与游戏" %(self.mode))
        else:
            self.start_game_without_promt(cmd_msg)

    def start_game_without_promt(self, cmd_msg):
        self.roles[0].send_start_msg()
        self.is_starting = True



    def stop_game_with_promt(self, cmd_msg):
        if True == self.is_starting:
            if "y" == self.input("是否停止游戏(y-是, n-否)"):
                self.stop_game_without_promt(cmd_msg)


    def stop_game_without_promt(self, cmd_msg):
        self.is_starting = False

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
        if False == self.is_starting:
            self.output("游戏还没开始运行")
        elif len(cmd_msg.contents) < 3 or \
            False == CmdController.is_int(cmd_msg.contents[1]) or \
            False == CmdController.is_int(cmd_msg.contents[2]):
            self.output("[put_down] 后面紧跟行号和列号")
        else:
            self.put_down_without_promt(cmd_msg)


    def put_down_without_promt(self, cmd_msg):
        row = int(cmd_msg.contents[1])
        col = int(cmd_msg.contents[2])


    def exit_with_promt(self, cmd_msg):
        if True == self.is_starting and 'y' == self.input("您正处于运行状态,是否要离开?(y-是, n-否)"):
            self.output("拜拜!")
            self.exit_without_promt(cmd_msg)
        else:
            self.output("拜拜!")
            self.exit_without_promt(cmd_msg)


    def exit_without_promt(self, cmd_msg):
        self.is_starting = False
        self.is_running = False

        exit(0)

    def show_chess(self, cmd_msg):
        if False == self.is_starting:
            self.output("游戏还没开始")
        else:
            print "xxxx"

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
        while(True):
            line = self.input("")
            if "" == line:
                continue

            cmd_msg = CmdMsg(line)
            if False == self.handles.has_key(cmd_msg.contents[0]):
                self.output("无效的命令")
            else:
                self.handles[cmd_msg.contents[0]](cmd_msg)


    def recv_msg(self, msg, watch_file):
        if msg.msg_type == ModuleMsg.PROMT_MSG_TYPE:
            watch_file.write(msg.content[0])
            watch_file.flush()
        elif msg.msg_type == ModuleMsg.EXIT_MSG_TYPE:
            self.is_exit = True


    def work_thread(self):
        inputs = [self.interface_in]
        outputs = []
        timeout = 1
        self.is_exit = False
        watch_file = open("watch_%d_%s.log" %(self.work.ident, self.nickname), 'w')
        while False == self.is_exit:
            readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
            if readable or writable or exceptional:
                for fd in readable:
                    if fd is self.interface_in:
                        msg = ModuleMsg().recv(fd)
                        self.recv_msg(msg)

        for role in self.roles:
            role.work.join()

        watch_file.close()
        self.is_starting = False
        self.roles = [None, None]



    def run(self):
        self.input_nickname()
        self.work = Thread(target = self.work_thread)
        self.interact()
        self.is_exit = False
        self.work.join()
        self.is_exit = True
