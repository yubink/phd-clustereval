#! /usr/bin/env python
# -*- coding: utf-8 -*-
#~/clustereval/eval$ python make_paper_eg.py ../data/maps/gov2/rrand/run_7/size ../data/maps/gov2/qkld_qinit/run_7/size ../data/maps/gov2/rrand/run_7/slidefuseMAPqrels_with_shard.out ../data/maps/gov2/qkld_qinit/run_7/slidefuseMAPqrels_with_shard.out

import sys
import pprint
import argparse
from collections import defaultdict

from sklearn import metrics
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

def read_size(fname):
    shard_sizes = dict()

    # read in shard sizes
    total_docs = 0
    for line in open(fname):
        shardno, size = line.split()
        tmp = shardno
        shardno = size
        size = tmp
        if shardno == "total":
            continue

        shard_sizes[shardno] = int(size)
        total_docs += int(size)
        #total_docs += 250000

    return shard_sizes


def read_infile(fname):
    shard_doc_cnt = defaultdict(lambda: defaultdict(int))

    num_qrys = 0
    curr_q = None 
    cnt = 0
    for line in open(fname):
        qnum, q0, docno, rel, shard = line.split()
        if int(rel) <= 0:
            continue

        if qnum != curr_q:
            num_qrys += 1
            curr_q = qnum
            cnt = 0

        shard_doc_cnt[qnum][shard] += 1
        cnt += 1
    return shard_doc_cnt


def gen_line(shard_sizes, shard_doc_cnt, qnum):
    shardcnts = shard_doc_cnt[qnum]

    sorted_cnts = sorted(shardcnts.items(), key=lambda x: x[1], reverse=True)
    xvals = [shard_sizes[sorted_cnts[0][0]]]
    yvals = [sorted_cnts[0][1]]
    tot_retrieved = yvals[0] 
    for idx, shard_cnts in enumerate(sorted_cnts[1:], start=1):
        # total of shard docs seen, is current shard size + all other
        # shard's sizes
        xvals.append(xvals[idx-1]+shard_sizes[shard_cnts[0]])
        yvals.append(yvals[idx-1]+shard_cnts[1])

        tot_retrieved += shard_cnts[1]

    total_docs = sum(shard_sizes.values())
    xvals = [x/float(total_docs) for x in xvals]
    yvals = [y/float(tot_retrieved) for y in yvals]

    if len(xvals) < len(shard_sizes):
        xvals.append(1.0) 
        yvals.append(1.0)

    # pretend shard sizes are all the same
    xvals = [x/float(len(yvals)) for x in  range(1, len(yvals)+1)]
    
    xvals = [0] + xvals
    yvals = [0] + yvals
        
    xvals = np.array(xvals)
    yvals = np.array(yvals)

    return (xvals, yvals)


if __name__ == '__main__':
    # Query 789 from run7 from qkld_qinit and rrand

    #pp = pprint.PrettyPrinter(indent=2)
    #avals = dict()
    #for line in open(sys.argv[1]):
    #    if len(line.split()) < 2:
    #        continue
    #    qnum, val = line.split()
    #    avals[qnum] = float(val)

    #bvals = dict()
    #for line in open(sys.argv[2]):
    #    if len(line.split()) < 2:
    #        continue
    #    qnum, val = line.split()
    #    bvals[qnum] = float(val)

    #diffs = []
    #for qnum, val in avals.items():
    #    diffs.append((qnum, bvals[qnum]-val))

    #pairs = sorted(diffs, cmp=lambda x,y: cmp(x[1],y[1]), reverse=True)
    #pp.pprint(pairs[0:10])

    parser = argparse.ArgumentParser()

    parser.add_argument('mapsize1', help='File containing size of shards.')
    parser.add_argument('mapsize2', help='File containing size of shards.')
    parser.add_argument('infile1', help='Shard annotated high accuracy result\
            list.')
    parser.add_argument('infile2', help='Shard annotated high accuracy result\
            list.')
    args = parser.parse_args()

    sz1 = read_size(args.mapsize1)
    sz2 = read_size(args.mapsize2)

    sdc1 = read_infile(args.infile1)
    sdc2 = read_infile(args.infile2)


    mpl.rcParams.update({'font.size': 9})

    from matplotlib import rcParams
    rcParams.update({'figure.autolayout': True})

    fig = plt.figure(figsize=(4,3), dpi=100)
    ax = fig.add_subplot(111)
    plt.xlabel("k")
    plt.ylabel("R_q(p, k)")

    xvals, yvals = gen_line(sz1, sdc1, '789')
    ax.plot(xvals, yvals, 'b--', label='Shard map A')
    xvals, yvals = gen_line(sz2, sdc2, '789')
    ax.plot(xvals, yvals, 'r:', label='Shard map B')

    ax.plot([0,1], [0,1], 'k-', label='Shard map C')

    ax.legend(loc='lower right')

    fig.savefig('wsdmeg.pdf')
