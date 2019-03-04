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
    parser.add_argument('-a', '--aucs', nargs='*', help='AUC files to compare. Order should be same as qevals.')
    parser.add_argument('-q', '--qevals', nargs='*', help='Qeval files to compare. Order should be same as aucs.')
    args = parser.parse_args()


    # should do macro vs micro averaging across queries maps
    # correlation should be across maps for the same queries. 

    if len(args.aucs) != len(args.qevals):
        raise ArgumentError('Number of AUC files provided aren\'t the same as Qeval files.')

    qevals = []
    aucs = []
    for idx, qf in enumerate(args.qevals):
        qeval_dict = qfiles.read_qeval(qf)

        auc_dict = dict()
        for line in open(args.aucs[idx]):
            arr = line.split()
            if len(arr) == 1:
                qnum = 'all'
                auc = arr[0]
            else:
                qnum = arr[0]
                auc = arr[1]

            auc_dict[qnum] = float(auc)

        qevals.append(qeval_dict)
        aucs.append(auc_dict)


    data_rows = []
    non_nan_cnts = 0
    avg_corr = 0
    qnums = qevals[0].keys()
    qnums.remove('all')

    #for qnum in sorted(qnums):
    #    qarr = []
    #    aarr = []
    #    for idx, qdict in enumerate(qevals):
    #        qval = 0
    #        if args.metric in qdict[qnum]:
    #            qval = qdict[qnum][args.metric]
    #        else:
    #            sys.stderr.write('%s had no value\n'%qnum)

    #        qarr.append(qval)
    #        aarr.append(aucs[idx][qnum])

    #    #print(qarr)
    #    #print(aarr)

    #    corr = pearsonr(qarr, aarr)
    #    if not math.isnan(corr[0]):
    #        avg_corr += corr[0]
    #        non_nan_cnts += 1

    #    avg_num_rel_ret = reduce(lambda memo, qdict: memo+qdict[qnum]['num_rel_ret'], qevals, 0.0)/float(len(qevals))
    #    data_rows.append([qnum, corr[0], np.mean(qarr), np.std(qarr), avg_num_rel_ret, ["%.4f"%x for x in qarr], ["%.4f" % x for x in aarr]])
    #    #print(qnum+' '+str(corr[0])+' '+str(np.mean(qarr))+' '+str(np.std(qarr))+' '+str(avg_num_rel_ret)+'/'+str(qevals[0][qnum]['num_rel'])) 

    #data_rows.sort(key=lambda x: x[3])
    ##pp.pprint(data_rows)
    #print('50percentile micro='+str(reduce(lambda memo, row: row[1]+memo, data_rows[len(data_rows)//2:], 0.0)/(len(data_rows)//2)))
    #print('Non-NAN micro corr='+str(avg_corr/non_nan_cnts))

    qarr = []
    aarr = []

    # figure out which pairs have statistically significant differences and calculate %age
    # draw a graphic with y-axis: each type of map, x-axis mean+conf. interval of metrics ordered the same way

    for idx, qdict in enumerate(qevals):
        qarr.append(qdict['all'][args.metric])
        aarr.append(aucs[idx]['all'])
    corr = pearsonr(qarr, aarr)

    # contingency table for cohen's kappa of significance tests
    c_table = np.zeros(shape=(3,3))
    addit_sig = 0
    #q_sig = 0
    #a_sig = 0
    #none_sig = 0
    #wrong_order = 0

    all_cnt = 0
    for pairs in itertools.combinations(enumerate(qevals), 2):
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

        auc_qnums = aucs[0].keys()
        auc_qnums.remove('all')
        for qnum in auc_qnums:
            aa.append(aucs[idx_a][qnum])
            ab.append(aucs[idx_b][qnum])

        # test if qevals metric difference is statistically significant
        statistic, qpval = ttest_rel(qa, qb)
        statistic, apval = ttest_rel(aa, ab)

        # build up contingency table for the statistical significance agreements
        m_a = qdict_a['all'][args.metric]
        m_b = qdict_b['all'][args.metric]
        auc_a = aucs[idx_a]['all'] 
        auc_b = aucs[idx_b]['all']

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

    #print('r\tpairs_recall\to+a')
    print('& $%.2f$ & $%d/%d=%.2f$ & $%.2f+%.2f=%.2f$ \\\\' % (corr[0], \
        c_table[0,0]+c_table[2,2], \
        sum(c_table[0,:])+sum(c_table[2,:]), \
        (c_table[0,0]+c_table[2,2])/float(sum(c_table[0,:])+sum(c_table[2,:])),\
        p_o,\
        addit_sig/all_cnt,\
        p_o+(addit_sig/all_cnt)\
        ))

    pp.pprint(c_table)
    print('Macro corr='+str(corr))
    print('p_o=%.3f p_e=%.3f Kappa = %.3f' % (p_o, p_e, ((p_o-p_e)/(1-p_e))))
    print('strong dis=%.3f ' % ((c_table[0,2]+c_table[2,0])/all_cnt))
    print('perc of sig found=%.3f ' % ((c_table[0,0]+c_table[2,2])/float(sum(c_table[0,:])+sum(c_table[2,:]))))
    print('addit sig=%.3f ' % (addit_sig/all_cnt))
    print('strong agree+addit sig=%.3f ' % (p_o+(addit_sig/all_cnt)))
    # % strong aggreeement
    # strong disaggreement (b>a sig, a<b sig)
    # % of sig found
    # additional sig where direction is same
    #print('% of qdiff found=%.3f, sig in same dir=%.3f (%.3f sig agree), ' % )
    #print('Agree %=%.3f (%.3f sig agree), ' % )
    #p_o = (c_table[0,0]+none_sig)/float(wrong_order+both_sig+none_sig+a_sig+q_sig)
    #print('Agree: %.3f' % ((both_sig+none_sig)/float(wrong_order+both_sig+none_sig+a_sig+q_sig)))
    #print('Both %d, None %d, Qeval %d, AUC %d, Wrong %d' % (both_sig, none_sig, q_sig, a_sig, wrong_order))

    qsorted = sorted(zip(qarr, args.aucs))
    asorted = sorted(zip(aarr, args.aucs))

    print('qeval vals: '+str([ "%.4f" % qval for qval,qf in qsorted]))
    print('qeval order: '+str([path.basename(path.dirname(qf)) for qval,qf in qsorted]))
    print('aeval vals: '+str([ "%.4f" % qval for qval,qf in asorted]))
    print('auc order: '+str([path.basename(path.dirname(af)) for aval,af in asorted]))


