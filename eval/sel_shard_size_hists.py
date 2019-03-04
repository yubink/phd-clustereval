#! /usr/bin/env python

import os
import os.path as path
import sys
import argparse
from collections import defaultdict
import math

import pprint
import numpy as np
from scipy.stats import pearsonr

import qfiles

# Correlates AUC results for queries and Qeval results for multiple runs?


if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=2)
    parser = argparse.ArgumentParser()
    parser.add_argument('shardrank', help='Shard rank list.')
    parser.add_argument('sizefile', help='Shard size file.')
    parser.add_argument('-i', '--invert', action='store_true', help='Invert\
            size file order to "num_docs shard_id" rather than "shard_id\
            num_docs"')
    args = parser.parse_args()

    sel_shards = []
    max_len = 0
    for line in open(args.shardrank):
        arr = line.split()
        qnum = arr[0]
        sel_shards = arr[1:]
        if len(sel_shards) > max_len:
            max_len = len(sel_shards)
        sel_shards.append(sel_shards)

    for row in sel_shards:
        if len(row) < max_len:
            row.append([0]*(max_len-len(row)))

    total_docs = 0
    for line in open(args.mapsize):
        shardno, size = line.split()
        if args.invert:
            tmp = shardno
            shardno = size
            size = tmp
            if shardno == "total":
                continue
        shard_sizes[shardno] = int(size)
        total_docs += int(size)

    shard_m = np.matrix(sel_shards)

