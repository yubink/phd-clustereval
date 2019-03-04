
from collections import defaultdict
from os import mkdir
import os.path as path
import sys
import argparse
import pprint

# for each query
# return top shard
# how many docs that appear in multiple queries? list.


if __name__ == '__main__':
    pp = pprint.PrettyPrinter()
    parser = argparse.ArgumentParser()

    parser.add_argument('outdir', help='Location for output shardmaps and shard-annotated qrels.')
    parser.add_argument('infile', help='Initial annotated qrels to base faked maps from.')
    parser.add_argument('shardlist', help='List of shards so you can create empty shards too.')
    args = parser.parse_args()

    all_shards = []
    for line in open(args.shardlist):
        all_shards.append(line.strip())


    ratios = [[100],[75,25],[50,50],[70,20,10],[50,35,15],[50,25,25],[34,33,33]]
    for ratio in ratios:
        for i in range(1, len(ratio)):
            ratio[i] += ratio[i-1]

    print(ratios)
    
    max_ratio_len = reduce(lambda maxval, curr: max(maxval, len(curr)), ratios, 0)
    
    # read the input file, determine best shard for each query
    # store documents current shard location
    multidocs = defaultdict(lambda: [])
    shardcount = defaultdict(int)
    best_shards = dict()
    query_docs = defaultdict(lambda: [])

    currqnum = 0
    rank = 0
    for line in open(args.infile):
        qnum, zero, docno, rel, shard = line.split()
        query_docs[qnum].append(docno)

        if qnum != currqnum:
            if currqnum != 0:
                best_shardpair = sorted(shardcount.items(), key=lambda x: x[1], reverse=True)[0:max_ratio_len]
                #print(currqnum+' '+str(best_shardpair))
                best_shards[currqnum] = [x[0] for x in best_shardpair]

            shardcount = defaultdict(int)
            currqnum = qnum
            rank = 0

        # ranks are 0 indexed for ratio_pos calculation purposes; see below
        multidocs[docno].append((rank, qnum))
        rank += 1
        if rank <= 1000:
            shardcount[shard] += 1 

    # for documents that appear in multiple queries, determine which query it "belongs" to
    # pick the query where it appeared highest in rank and also store its rank in that query
    doc_tiebreaker = dict()
    for docno, qnums in multidocs.items():
        if len(qnums) > 1:
            doc_tiebreaker[docno] = sorted(qnums)[0]

    # create folder and instantiate files for partial shard maps
    # generate new partial shard maps for the documents we've seen; necessary for rbr/rank-s etc
    for ratio in ratios:
        dirname = path.join(args.outdir, '-'.join(map(str,ratio)))
        if not path.exists(dirname):
            mkdir(dirname)


    # pick top N shards for each query
    best_shardpair = sorted(shardcount.items(), key=lambda x: x[1], reverse=True)[0:max_ratio_len]
    #print(qnum+' '+str(best_shardpair[0]))
    best_shards[qnum] = [x[0] for x in best_shardpair]

    # generate the new fake shards; the qrels output and the "shardmap"
    written_docs = set()
    for ratio in ratios:
        with open(path.join(args.outdir,'-'.join(map(str,ratio))+'.qrel'), 'w') as wf:

            shardoutfs = dict()
            for shard in all_shards:
                shardoutfs[shard] = open(path.join(args.outdir,('-'.join(map(str,ratio))),shard), 'w')

            for qnum, docs in sorted(query_docs.items()):
                for i, doc in enumerate(docs):

                    if doc in doc_tiebreaker: 
                        ref_rank, ref_qnum = doc_tiebreaker[doc]
                    else:
                        ref_rank = i
                        ref_qnum = qnum

                    curr_ratio = ref_rank*100//len(docs)
                    ratio_pos = next(pos for pos, num in enumerate(ratio) if num >= curr_ratio)
                    outshard = best_shards[ref_qnum][ratio_pos]

                    if doc not in written_docs:
                        shardoutfs[outshard].write('%s\n' % doc)
                        written_docs.add(doc)
                    wf.write('%s 0 %s 1 %s\n' % (qnum, doc, outshard))

            for sf in shardoutfs.values():
                sf.close()



    #totnum = 0
    #for docno, qlist in sorted(multidocs.items(), key=lambda x: len(x[1]), reverse=True):

    #    if len(qlist) > 1:
    #        totnum+=1
    #        print(docno+' '+str(qlist))

    #print('total %d/%d'%(totnum,len(multidocs)))


