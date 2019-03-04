#! /usr/bin/env python

import os
import os.path as path
import sys
import argparse
import random


# need to read map files and combine it with search files and figure out which
# shards have the docs we want

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('shardlist', help='File containing list of shard ids.')
    parser.add_argument('outdir', help='Output directory.')
    parser.add_argument('searchfiles', nargs='*', help='TREC output file that\
            we need to annotate for shards.')

    args = parser.parse_args()

    shardlist = []
    for line in open(args.shardlist):
        shardlist.append(line.strip())

    for searchfile in args.searchfiles:
        fname = path.basename(searchfile)
        #print(path.join(args.outdir, fname))

        outf = open(path.join(args.outdir, fname), 'w')
        for line in open(searchfile):
            qnum, q0, docno, rank, score, dummy = line.split()
            outf.write(line.strip()+' '+random.choice(shardlist)+'\n')

