#! /bin/sh

for i in {1..10} 
do python map_req_docs.py /bos/data0/ss_maps/cikm2016_dai/qkld_qinit/gov2/run_$i output_qinit_run$i ../fusion/output/*.out &
  python map_req_docs.py /bos/data0/ss_maps/cikm2016_dai/qkld_rand/gov2/run_$i output_rand_run$i ../fusion/output/*.out &
  
done

