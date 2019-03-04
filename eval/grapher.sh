#! /bin/sh

for i in {1..10} 
do for j in output_qinit_run$i/slidefuseMAP*.out
  do python recall_vs_eff.py /bos/data0/ss_maps/cikm2016_dai/qkld_qinit/gov2/run_$i/size $j -o output_qinit_run$i -i > ${j}.fakesize.value
  done
done

#for i in {1..10} 
#  do for j in output_rand_run$i/*.out
#  do python recall_vs_eff.py /bos/data0/ss_maps/cikm2016_dai/qkld_rand/gov2/run_$i/size $j -o output_rand_run$i -i > ${j}.value
#  done
#done
