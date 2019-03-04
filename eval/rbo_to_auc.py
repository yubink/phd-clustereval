#! /usr/bin/env python

import os
import os.path as path
import sys
import argparse
from collections import defaultdict
import math
import itertools

import pprint
import numpy as np
import re

import qfiles

# turns rbo files into auc output files 

if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=2)
    parser = argparse.ArgumentParser()
    parser.add_argument('rbofile', help='rbo file to convert')
    parser.add_argument('-p', '--param', dest='param', default='0.999',
            help='RBO depth parameter to extract')
    args = parser.parse_args()

    for line in open(args.rbofile):
        if line.startswith(args.param):
            dat_arg = line.split()[1:]
            if re.match(r'\d+', dat_arg[0]) is not None:
                print(' '.join(dat_arg))
            elif dat_arg[0] == 'Avg':
                print(dat_arg[1])


