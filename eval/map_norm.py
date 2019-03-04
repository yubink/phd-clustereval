
from random import randint
from collections import defaultdict
from os import mkdir
import os.path as path
import sys
import argparse
import pprint

import numpy as np
from sklearn import metrics

def num_shard_norm(num):
    yvals = [0] + [1]*num
    xvals = [x/float(num) for x in range(num+1)]

    xvals = np.array(xvals)
    yvals = np.array(yvals)

    return metrics.auc(xvals, yvals)


def shard_size_norm(size_list):
    size_list = sorted(size_list)

    total = float(sum(size_list))

    xvals = [0] 
    for idx, val in enumerate(size_list):
        xvals.append(xvals[idx]+val/total)

    yvals = [0] + [1]*len(size_list)

    xvals = np.array(xvals)
    yvals = np.array(yvals)

    return metrics.auc(xvals, yvals)



if __name__ == '__main__':
    print(shard_size_norm([250,250,250,250]) )
    print('hi')
