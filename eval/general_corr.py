
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
from scipy.stats import pearsonr
from scipy.stats import ttest_rel

import qfiles

# Correlates AUC results for queries and Qeval results for multiple runs?


if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=2)
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--metric', dest='metric', default='map', help='Metric in Qeval file to use.')
    parser.add_argument('-a', '--aevals', nargs='*', help='Qeval files of\
        system A. Order should be same as bevals.')
    parser.add_argument('-b', '--bevals', nargs='*', help='Qeval files of\
        system B. Order should be same as aevals.')
    args = parser.parse_args()


    if len(args.aevals) != len(args.bevals):
        raise ArgumentError('Number of AUC files provided aren\'t the same as Qeval files.')

    bevals = []
    aevals = []
    for idx, bf in enumerate(args.bevals):
        beval_dict = qfiles.read_qeval(bf)
        aeval_dict = qfiles.read_qeval(args.aevals[idx])

        bevals.append(beval_dict)
        aevals.append(aeval_dict)

    barr = []
    aarr = []
    for idx, qdict in enumerate(bevals):
        barr.append(qdict['all'][args.metric])
        aarr.append(aevals[idx]['all'][args.metric])
    corr = pearsonr(barr, aarr)
    print('Macro corr='+str(corr))

    # contingency table for cohen's kappa of significance tests
    c_table = np.zeros(shape=(3,3))
    addit_sig = 0
    #q_sig = 0
    #a_sig = 0
    #none_sig = 0
    #wrong_order = 0

    qnums = bevals[0].keys()
    qnums.remove('all')

    all_cnt = 0
    for pairs in itertools.combinations(enumerate(bevals), 2):
        all_cnt += 1

        idx_a = pairs[0][0]
        idx_b = pairs[1][0]

        qdict_a = pairs[0][1]
        qdict_b = pairs[1][1]
        
        # qeval vals
        qa = []
        qb = []
        # auc vals
        aa = []
        ab = []

        # run two-sided paired t-test for metric and AUC
        for qnum in qnums:
            qa.append(qdict_a[qnum][args.metric])
            qb.append(qdict_b[qnum][args.metric])

            aa.append(aevals[idx_a][qnum][args.metric])
            ab.append(aevals[idx_b][qnum][args.metric])

        # test if qevals metric difference is statistically significant
        statistic, qpval = ttest_rel(qa, qb)
        statistic, apval = ttest_rel(aa, ab)

        # build up contingency table for the statistical significance agreements
        m_a = qdict_a['all'][args.metric]
        m_b = qdict_b['all'][args.metric]
        auc_a = aevals[idx_a]['all'][args.metric]
        auc_b = aevals[idx_b]['all'][args.metric]

        c_i = c_j = 0
        if qpval < 0.05:
            if m_a > m_b:
                c_i = 0
            else:
                c_i = 2
        else:
            c_i = 1

        if apval < 0.05:
            if auc_a > auc_b:
                c_j = 0
            else:
                c_j = 2
        else:
            c_j = 1

        # count instances where AUC says difference is sig
        # and the original metric has the same ordering between a and b,
        # but decides the difference isn't significant
        # basically the cases where additional significance is found.
        if c_i == 1 and c_j == 0 and m_a > m_b or \
                c_i == 1 and c_j == 2 and m_b > m_a:
            addit_sig += 1


        c_table[c_i,c_j] += 1

    all_cnt = float(all_cnt)
    p_o = (c_table[0,0]+c_table[1,1]+c_table[2,2])/all_cnt
    p_e = (sum(c_table[0])/all_cnt)*(sum(c_table[:,0])/all_cnt) +\
        (sum(c_table[1])/all_cnt)*(sum(c_table[:,1])/all_cnt) +\
        (sum(c_table[2])/all_cnt)*(sum(c_table[:,2])/all_cnt)

    pp.pprint(c_table)
    print('p_o=%.3f p_e=%.3f Kappa = %.3f' % (p_o, p_e, ((p_o-p_e)/(1-p_e))))
    print('strong dis=%.3f ' % ((c_table[0,2]+c_table[2,0])/all_cnt))
    print('perc of sig found=%.3f ' % ((c_table[0,0]+c_table[2,2])/float(sum(c_table[0,:])+sum(c_table[2,:]))))
    print('addit sig=%.3f ' % (addit_sig/all_cnt))
    print('strong agree+addit sig=%.3f ' % (p_o+(addit_sig/all_cnt)))

    qsorted = sorted(zip(barr, args.aevals))
    asorted = sorted(zip(aarr, args.aevals))

    print('qeval vals: '+str([ "%.4f" % qval for qval,qf in qsorted]))
    print('qeval order: '+str([path.basename(path.dirname(qf)) for qval,qf in qsorted]))
    print('aeval vals: '+str([ "%.4f" % qval for qval,qf in asorted]))
    print('auc order: '+str([path.basename(path.dirname(af)) for aval,af in asorted]))

