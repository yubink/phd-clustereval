import sys

currq = 0
has_one = False
for line in open(sys.argv[1]):
    qnum, zero, docno, score = line.split()

    if qnum != currq:
        if currq != 0 and not has_one:
            print(currq)
        currq = qnum
        has_one = False

    if not has_one and int(score) > 0:
        has_one = True

    

