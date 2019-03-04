#! /usr/bin/env python

import sys
import numpy as np
from sklearn import metrics

def boopydoop(butt):
    butt += 1
    return butt
    

if __name__ == "__main__":
    arr = np.array([1,2,3])
    print(arr)
    print(boopydoop(4))
    print("hello world")

    for line in open("testf"):
        print(line.strip())

    f = open('buttface', 'w')
    f.write('butt\n')
    f.close()
    
