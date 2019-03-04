#! /usr/bin/env python

import os
import os.path as path
import sys
import argparse
import operator
from collections import defaultdict

import numpy as np
from scipy.stats import ttest_rel


# this does the ttests between query init shard maps, rand init shard maps intra and inter.


if __name__ == '__main__':
    # read in all data
    qinit_dat = dict()
    rand_dat = dict()
    for i in range(1,11):
        qdat = dict()
        for line in open(path.join('output_qinit_run%d'%i, 'slidefuseMAP.out.value')):
            pair = line.split()
            if len(pair) == 2:
                qdat[pair[0]] = float(pair[1])
        qinit_dat[i] = qdat

        rdat = dict()
        for line in open(path.join('output_rand_run%d'%i, 'slidefuseMAP.out.value')):
            pair = line.split()
            if len(pair) == 2:
                rdat[pair[0]] = float(pair[1])
        rand_dat[i] = rdat

    qnum_order = list(qinit_dat[1].keys())

    for i, qdat in qinit_dat.items():
        qarray_vals = []
        rarray_vals = []
        for qnum in qnum_order:
            qarray_vals.append(qdat[qnum])
            rarray_vals.append(rand_dat[i][qnum])
        qinit_dat[i] = qarray_vals
        rand_dat[i] = rarray_vals

    intra_res = []
    intra_res_q = []
    inter_res = []
    intra_sig_cnt = 0
    intra_sig_cnt_q = 0
    inter_sig_cnt = 0
    for i in range(1,11):
        for j in range(1,11):
            stats, qr = ttest_rel(qinit_dat[i], rand_dat[j])
            inter_res.append((i, j, qr))
            if qr < 0.05:
                inter_sig_cnt += 1
            #print('q%d r%d %f' % (i, j, qr))

            if i != j:
                stats, qq = ttest_rel(qinit_dat[i], qinit_dat[j])
                #print('q%d q%d %f' % (i, j, qq))
                intra_res_q.append('q%d q%d %f' % (i, j, qq))
                if qq < 0.05:
                    intra_sig_cnt_q += 1

                stats, rr = ttest_rel(rand_dat[i], rand_dat[j])
                #print('r%d r%d %f' % (i, j, rr))
                intra_res.append('r%d r%d %f' % (i, j, rr))
                if rr < 0.05:
                    intra_sig_cnt += 1


    for res in inter_res:
        print('q%d r%d %f' % res)
    print('%d out of %d = %f' % (inter_sig_cnt, len(inter_res), inter_sig_cnt/float(len(inter_res))))

    print()

    for res in intra_res_q:
        print(res)
    print('%d out of %d = %f' % (intra_sig_cnt_q, len(intra_res_q), intra_sig_cnt_q/float(len(intra_res_q))))

    for res in intra_res:
        print(res)
    print('%d out of %d = %f' % (intra_sig_cnt, len(intra_res), intra_sig_cnt/float(len(intra_res))))

