#!/usr/bin/bash

import os
import sys
import re
import getopt


class GetOpt(object):
    @staticmethod
    def get_args(usage):
        short_args = []
        long_args = []
        str = usage.split('usage:')[1]
        for arg in str.split('\n'):
            arg = re.search(r'\[(.*)\].*', arg)
            if None != arg:
                arg = arg.group(1)
                if True == arg.startswith('--'):
                    long_args.append(arg[2:])
                elif True == arg.startswith('-'):
                    short_args.append(arg[1:])

        return (short_args, long_args)


    @staticmethod
    def get_opt(usage):
        opt_args = {}
        try:
            (short_args, long_args) = GetOpt.get_args(usage)
            opts, args = getopt.getopt(sys.argv[1:], ''.join(short_args), long_args)

            for opt, arg in opts:
                if "--help" == opt or "-h" == opt:
                    print usage;
                    exit(0)

                opt_args[opt] = arg

        except getopt.GetoptError:
            print usage
            exit(0)

        return opt_args
