import re
import sys
import pprint
import random
import argparse
from collections import defaultdict

from sklearn import metrics
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

pp = pprint.PrettyPrinter(indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('aurecf', help='File containing aurec info.')
    parser.add_argument('ranksf', help='File containing ranks info.')
    args = parser.parse_args()

    aurecd = defaultdict(lambda: dict())
    ranksd = defaultdict(lambda: dict())
#qkld_qinit_run10/slidefuseMAP.out.nosize.value 701 0.871510638298
#gov2-qkld-qinit/run_10/gov2.Qeval:P_1000	701	0.0683

    p = re.compile(r'run(\d+)')
    for line in open(args.aurecf):
        run = p.search(line).group(1)
        cols = line.split()
        if 'qkld' in line and 'qinit' in line:
            aurecd['qinit_'+run][cols[1]] = float(cols[2])
        elif 'qkld' in line and 'rand' in line:
            aurecd['qrand_'+run][cols[1]] = float(cols[2])
        else:
            aurecd['rrand_'+run][cols[1]] = float(cols[2])
            
    xvals = []
    yvals = []

    p = re.compile(r'run_(\d+)')
    for line in open(args.ranksf):
        run = p.search(line).group(1)
        cols = line.split()

        if 'qkld' in line and 'qinit' in line:
            akey = 'qinit_'+run
        elif 'qkld' in line and 'rand' in line:
            akey = 'qrand_'+run
        else:
            akey = 'rrand_'+run

        xval = aurecd[akey][cols[1]]
        if xval:
            xvals.append(xval)
            yvals.append(float(cols[2]))


    idxs = np.random.choice(len(xvals), 200)

    xvals_s = [xvals[i] for i in idxs]
    yvals_s = [yvals[i] for i in idxs]

    mpl.rcParams.update({'font.size': 9})

    from matplotlib import rcParams
    rcParams.update({'figure.autolayout': True})

    fig = plt.figure(figsize=(4,3), dpi=100)
    ax = fig.add_subplot(111)
    plt.xlabel("AUReC")
    plt.ylabel("P@1000")

    ax.scatter(xvals_s, yvals_s)

    #ax.legend(loc='lower right')

    fig.savefig('ictireg.pdf')
