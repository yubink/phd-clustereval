#! /usr/bin/env python

import os
import os.path as path
import sys
import argparse
import operator
from collections import defaultdict

import numpy as np
from scipy.stats import wilcoxon

# need to read map files and combine it with search files and figure out which
# shards have the docs we want

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('base', help='Baseline')
    parser.add_argument('tocompare', help='Compare')
    args = parser.parse_args()

    base_vals = dict()
    for line in open(args.base):
        pair = line.split()
        if len(pair) == 2:
            base_vals[pair[0]] = float(pair[1])

    comp_vals = dict()
    for line in open(args.tocompare):
        pair = line.split()
        if len(pair) == 2:
            comp_vals[pair[0]] = float(pair[1])

    x_vals = []
    y_vals = []
    for qnum, val in base_vals.items():
        x_vals.append(val)
        y_vals.append(comp_vals[qnum])

    #print(x_vals)
    #print(y_vals)
    stats, pval = wilcoxon(x_vals, y_vals)
    print(stats)
    print(pval)
    

