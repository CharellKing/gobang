#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys

class UserInfo(object):
    def __init__(self, nickname, win_times, fail_times):
        self.nickname = nickname
        self.win_times = win_times
        self.fail_times = fail_times

    def __str__(self):
        return "%s,%d,%d" %(self.nickname, self.win_times, self.fail_times)

    @staticmethod
    def rank_compare(one_user_info, other_user_info):
        ret = 0
        if (one_user_info.win_times - one_user_info.fail_times) > (other_user_info.win_times - other_user_info.fail_times):
            ret += 1

        elif (one_user_info.win_times - one_user_info.fail_times) < (other_user_info.win_times - other_user_info.fail_times):
            ret -= 1

        if (one_user_info.win_times > other_user_info.win_times):
            ret += 1

        elif (one_user_info.win_times < other_user_info.win_times):
            ret -= 1

        if (one_user_info.fail_times > other_user_info.fail_times):
            ret -= 1

        elif (one_user_info.fail_times < other_user_info.fail_times):
            ret += 1

        if (one_user_info.win_times + one_user_info.fail_times) > (other_user_info.win_times + other_user_info.fail_times):
            ret += 1

        elif (one_user_info.win_times + one_user_info.fail_times) < (other_user_info.win_times + other_user_info.fail_times):
            ret -= 1

        print ret
        return ret
