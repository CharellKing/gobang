#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys
import random


class Stone(object):
    WHITE = True
    BLACK = False

    def __init__(self, x_grid, y_grid, color):
        self.x_grid = x_grid
        self.y_grid = y_grid
        self.color = color

    def key(self):
        return self.x_grid << 8 | self.y_grid


class Gobang(object):
    GRIDS = 15

    SUCCESS = 1
    FAILED = 2
    TIED = 3
    UNKNOWN = 4

    RELAY_TIME = 5

    def __init__(self):
        self.stones = {}    #pos => stone
        self.stack = []     #stone stack


    def put_stone(self, x_grid, y_grid, color):
        if 0 <= x_grid < Gobang.GRIDS and \
            0 <= y_grid < Gobang.GRIDS and \
            False == self.is_taken_up(x_grid, y_grid):
            self.stones[x_grid << 8 | y_grid] = Stone(x_grid, y_grid, color)
            self.stack.append(self.stones[x_grid << 8 | y_grid])
            return True
        return False


    def count_line(self, x_grid, y_grid, x_inc, y_inc):
        count = 1
        x_up_grids = x_grid + x_inc
        y_up_grids = y_grid + y_inc
        while self.stones.has_key(x_up_grids << 8 | y_up_grids) and \
              self.stones[x_grid << 8 | y_grid].color == self.stones[x_up_grids << 8 | y_up_grids].color:
            count += 1
            x_up_grids += x_inc
            y_up_grids += y_inc



        x_down_grids = x_grid - x_inc
        y_down_grids = y_grid - y_inc
        while self.stones.has_key(x_down_grids << 8 | y_down_grids) and \
              self.stones[x_grid << 8 | y_grid].color == self.stones[x_down_grids << 8 | y_down_grids].color:
            count += 1
            x_down_grids -= x_inc
            y_down_grids -= y_inc

        return count

    def is_five(self, x_grid, y_grid):
        # \
        if self.count_line(x_grid, y_grid, 1, 1) >= 5:
            return True

        # /
        if self.count_line(x_grid, y_grid, 1, -1) >= 5:
            return True

        # -
        if self.count_line(x_grid, y_grid, 1, 0) >= 5:
            return True

        # |
        if self.count_line(x_grid, y_grid, 0, 1) >= 5:
            return True

        return False

    def is_tie(self, x_grid, y_grid):
        return len(self.stones) >= Gobang.GRIDS * Gobang.GRIDS

    def is_taken_up(self, x_grid, y_grid):
        return self.stones.has_key(x_grid << 8 | y_grid)

    def robot_stone(self, color):
        for x_grid in xrange(0, Gobang.GRIDS):
            for y_grid in xrange(0, Gobang.GRIDS):
                if False == self.stones.has_key(x_grid << 8 | y_grid):
                    self.stones[x_grid << 8 | y_grid] = Stone(x_grid, y_grid, color)
                    self.stack.append(self.stones[x_grid << 8 | y_grid])
                    return (x_grid, y_grid)
        return (None, None)

    def random_stone(self, color):
        for x_grid in xrange(0, Gobang.GRIDS):
            for y_grid in xrange(0, Gobang.GRIDS):
                if False == self.stones.has_key(x_grid << 8 | y_grid):
                    self.stones[x_grid << 8 | y_grid] = Stone(x_grid, y_grid, color)
                    self.stack.append(self.stones[x_grid << 8 | y_grid])
                    return (x_grid, y_grid)
        return (None, None)

    def get_last_stone():
        return self.stack[-1]

    @staticmethod
    def random_order():
        if 0 == random.randint(0, 1):
            return Stone.BLACK
        return Stone.WHITE
