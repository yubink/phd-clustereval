#! /usr/bin/env python

import os
import os.path as path
import sys
import argparse
import operator
import map_norm
from collections import defaultdict

from sklearn import metrics
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

# creates auc curves, saves it to a folder and outputs auc values

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('mapsize', help='File containing size of shards.')
    parser.add_argument('infile', help='Shard annotated high accuracy result\
            list.')
    parser.add_argument('-t', '--infile_type', dest='itype',
            default='retrieval', help='Input file type. retrieval or qrel')
    parser.add_argument('-o', '--outdir', dest='outdir', default='.', help='Place to output imgs')
    parser.add_argument('-i', '--invert', action='store_true', help='Invert\
            size file order to "num_docs shard_id" rather than "shard_id\
            num_docs"')
    parser.add_argument('-z', dest='norm_type', help='How to normalize AUC\
            values?', default='none', choices=['none','size-perc','num-perc',
                'size-sub', 'num-sub', 'nosize'])
    parser.add_argument('-l', '--limit', type=int, default=1000, help='Limit of\
            relevant documents to look at in infile.')
    parser.add_argument('-q', '--query_limit', type=int, default=-1, help='Limit of\
            number of queries to look at in infile.')
    args = parser.parse_args()

    shard_sizes = dict()

    # read in shard sizes
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
        #total_docs += 250000

    #calculate normalization constant
    if args.norm_type.startswith('size'):
        norm = map_norm.shard_size_norm(shard_sizes.values())
    elif args.norm_type.startswith('num'):
        norm = map_norm.num_shard_norm(len(shard_sizes))

    shard_doc_cnt = defaultdict(lambda: defaultdict(int))

    num_qrys = 0
    curr_q = None 
    cnt = 0
    for line in open(args.infile):
        if args.itype == 'retrieval':
            qnum, q0, docno, rank, score, dummy, shard = line.split()
        elif args.itype == 'qrel':
            qnum, q0, docno, rel, shard = line.split()
            if int(rel) <= 0:
                continue

        if qnum != curr_q:
            num_qrys += 1
            curr_q = qnum
            cnt = 0

        if cnt >= args.limit:
            continue

        if args.query_limit > 0 and num_qrys > args.query_limit:
            break
        shard_doc_cnt[qnum][shard] += 1
        cnt += 1



    #fig = plt.figure()
    #ax = fig.add_subplot(111)
    #plt.xlabel("frac. of corpus searched")
    #plt.ylabel("frac. of docs found")

    all_aucs = 0
    for qnum, shardcnts in shard_doc_cnt.items():

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

        xvals = [x/float(total_docs) for x in xvals]
        yvals = [y/float(tot_retrieved) for y in yvals]

        if len(xvals) < len(shard_sizes):
            xvals.append(1.0) 
            yvals.append(1.0)

        if args.norm_type == 'nosize': 
            # pretend shard sizes are all the same
            xvals = [x/float(len(yvals)) for x in  range(1, len(yvals)+1)]
        
        xvals = [0] + xvals
        yvals = [0] + yvals
            
        xvals = np.array(xvals)
        yvals = np.array(yvals)

        auc = metrics.auc(xvals, yvals)

        if args.norm_type.endswith('sub'):
            auc = norm - auc
        elif args.norm_type.endswith('perc'):
            auc = auc/norm

        print(qnum+' '+str(auc))
        all_aucs += auc
        
        #ax.plot(xvals, yvals)


    avg_auc = all_aucs/len(shard_doc_cnt)
    print(avg_auc)
    #print(all_aucs)
    #fig.savefig(path.join(args.outdir, path.basename(args.infile)+'.'+args.norm_type+'.png'))

