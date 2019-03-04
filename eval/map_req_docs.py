#! /usr/bin/env python

import os
import os.path as path
import sys
import argparse


# need to read map files and combine it with search files and figure out which
# shards have the docs we want

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('mapdir', help='Directory for shardmap.')
    parser.add_argument('outdir', help='Output directory.')
    parser.add_argument('searchfiles', nargs='*', help='TREC output file that\
            we need to annotate for shards.')

    args = parser.parse_args()

    shardmap = dict()
    for root, dirs, files in os.walk(args.mapdir):
        for fname in files:
            #print(fname)
            for line in open(path.join(root, fname)):
                shardno = fname
                shardmap[line.strip()] = shardno
                

    for searchfile in args.searchfiles:
        fname = path.basename(searchfile)
        #print(path.join(args.outdir, fname))

        outf = open(path.join(args.outdir, fname), 'w')
        for line in open(searchfile):
            qnum, q0, docno, rank, score, dummy = line.split()
            outf.write(line.strip()+' '+shardmap[docno]+'\n')

