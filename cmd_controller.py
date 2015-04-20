#!/usr/bin/python
#-*-coding:utf-8-*-

import sys

from const_str import ConstStr
from human_role import HumanRole
from robot_role import RobotRole

class CmdMsg(object):
    JOIN_MODE = "join_mode"
    START_GAME = "start_game"
    STOP_GAME = "stop_game"
    PUT_DOWN = "put_down"
    EXIT_MODE = "exit_mode"
    EXIT = "exit"
    CHESS = "show_chess"
    HELP = "show_help"

    def __init_(self, cmd_msg):
        self.contents = cmd_msg.splite(' ')


class CmdController(object):
    def __init__(self, cmd_out):
        self.nickname = ""   #玩家昵称
        self.mode = ""      #模式人机对弈与网络对弈
        self.cmd_out = cmd_out

        self.roles = [None, None]

        self.cmd_msg = ""

        self.handles = {CmdMsg.JOIN_MODE: self.join_mode_with_promt,
                        CmdMsg.EXIT_MODE: self.exit_mode_with_promt,
                        CmdMsg.START_GAME: self.start_game_with_promt,
                        CmdMsg.STOP_GAME: self.exit_game_with_promt,
                        CmdMsg.PUT_DOWN: self.put_down_with_promt,
                        CmdMsg.EXIT: self.exit_with_promt,
                        CmdMsg.CHESS: self.show_chess,
                        CmdMsg.HELP: self.show_help}

        self.is_network_running = False #是否网络运行正常
        self.is_starting = False   #是否正在游戏


    def get_status(self):
        status = ""
        if "" != self.mode:
            status += self.mode
        if True == self.is_starting:
            self += ", 运行中"

    def join_mode_with_promt(self, cmd_msg):
        if len(cmd_msg) <= 1 or (cmd_msg.contents[1] != ConstStr.robotplay_mode and cmd_msg.contents[1] != ConstStr.netplay_mode):
            cmd_out.output("[cmd_error], 'join_mode' 后面应该紧跟正确的模式名称[%s|%s]" %(self.greet(), ConstStr.robotplay_mode,
                                                                                ConstStr.netplay_mode, ConstStr.robotplay_mode))
        elif cmd_msg.contents[1] != self.mode:
            if ('y' == raw_input("%s 你正处于[%s]状态,是否要离开?(y-yes, n-no)").strip('\n')):
                self.join_mode_without_promt(cmd_msg)

    def join_mode_without_promt(self, cmd_msg):
        if True == self.is_starting:
            print "xxx"

        self.is_starting = False

        self.mode = cmd_msg.contents[1]

        if ConstStr.robotplay_mode == self.mode:
            self.run_robotplay()
        else:
            self.run_netplay()



    def exit_mode_with_promt(self, cmd_msg):
        if "" != self.mode and
            ('y' == raw_input("%s 你正处于[%s]状态,是否要离开?(y-是, n-否)>" %(self.greet(), self.status())).strip('\n')):
            self.exit_mode_without_promt(cmd_msg)


    def exit_mode_without_promt(self, cmd_msg):
        if True == self.is_staring:
            print "xxx"

        self.is_starting = False
        self.mode = ""

    def start_game_with_promt(self, cmd_msg):
        if "" == self.mode:
            self.output("%s 还没有进入任何模式", %(self.greet()))
        elif ConstStr.netplay_mode == self.mode and False == self.is_network_running:
            self.output("%s 您处于%s, 没有发起或者参与游戏" %(self.greet(), self.mode))
        else:
            self.start_game_without_promt(cmd_msg)

    def start_game_without_promt(self, cmd_msg):
        print "xxx"

    def stop_game_with_promt(self, cmd_msg):
        if True == is_starting:
            self.output("%s 是否停止游戏" %(self.greet()))
            self.stop_game_without_promt(cmd_msg)


    def stop_game_without_promt(self, cmd_msg):
        print "xxxx"
        self.is_starting = False

    def is_int(self, str):
        try:
            int(str)
            return True
        except:
            return False

    def put_down_with_promt(self, cmd_msg):
        if False == is_starting:
            print "%s 游戏还没开始运行" %(self.greet())
        elif len(cmd_msg) < 3 or False == self.is_int(cmd_msg[1]) or False == self.is_int(cmd_msg[2]):
            print "%s put_down后面紧跟行号和列号" %(self.greet())
        else:
            self.put_down_with_promt(cmd_msg)


    def put_down_without_promt(self, cmd_msg):
        print "xxxx"


    def exit_with_promt(self, cmd_msg):
        if True == is_starting and
            ('y' == raw_input("%s 你正处于[%s]状态,是否要离开?(y-是, n-否)>" %(self.greet(), self.status())).strip('\n')):
             exit_without_promt(self, cmd_msg)

    def exit_without_promt(self, cmd_msg):
        self.is_starting = False
        self.is_running = False

    def show_chess(self, cmd_msg):
        if False == is_staring:
            self.output("%s 游戏还没有开始" %(self.greet()))
        else:
            print "xxxx"


    def show_help(self, cmd_msg):
        print "%s\n%s\n%s\n" %("join_mode   进入模式(人机对弈|网络对弈)\n",
                               "exit_mode   退出模式\n",
                               "start_game  开始游戏\n",
                               "stop_game   停止游戏\n",
                               "show_chess  显示棋局\n"
                               "put_down    落子(row, col)\n",
                               "exit        退出游戏\n",
                               "help        帮助")

    def greet(self):
        return "哈喽, %s!" %(self.nickname)

    def output(self, line):
        cmd_out.write(str)
        cmd_out.flush()

    def input_nickname(self):
        while None == self.nickname or "" == self.nickname:
            self.nickname = raw_input("请输入您的昵称>").strip('\n')
        self.output("%s 您的昵称是%s!\n" %(self.greet(), self.nickname))


    def select_mode(self):
        while None == self.mode or (ConstStr.netplay_mode != self.mode and ConstStr.robotplay_mode != self.mode):
            self.mode = raw_input("%s 请选择模式[%s|%s]>" %(self.greet(), ConstStr.netplay_mode, ConstStr.robotplay_mode)).strip('\n')
        self.output("%s 您选择的是%s!\n" %(self.greet(), self.mode))

        if ConstStr.netplay_mode == self.mode:
            self.run_netplay()
        else:
            self.run_robotplay()

    def cmd_promt(self):
        cmd_msg = None
        while "" == self.cmd_msg:
            self.cmd_msg = raw_input("%s 请输入命令:>" %(self.greet())).strip('\n')

        return CmdMsg(self.cmd_msg)


    def interact(self):
        while(True):
            cmd_msg = cmd_promt(self)
            if True == handles.has_key(cmd_msg.content[0]):
                handles[cmd_msg.content[0]](cmd_msg)
            else:
                self.output("%s 符号\n" %(self.greet())
                self.deal_help(cmd_msg)


    def run_robotplay(self):
        human_out , robot_in = popen2("human_out_robot_in", "wr");
        robot_out,  human_in = popen2("robot_out, human_in", "wr")

        self.roles[0] = HumanRole(human_in, human_out)
        self.roles[1] = RobotRole(robot_in, robot_out)


    def run_netplay(self):
        print "hello"

    def run(self):
        self.input_nickname()
