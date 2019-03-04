# quick file for calculating variance of shard maps

import numpy as np
import sys

for f in sys.argv[1:]:
    sizes = []
    print(f)
    for line in open(f):
        num, shardno = line.split()
        if shardno != "total":
            sizes.append(int(num))

    print(np.var(sizes))




