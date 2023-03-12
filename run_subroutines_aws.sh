#!/bin/bash

rm -rf ~/.cache/torch_extensions

start=`date +%s`

set -ex

python3 ctg_approx/avi.py --env cube3 --states_per_update 50000000 --batch_size 10000 --nnet_name cube3_subroutines --max_itrs 250000 --loss_thresh 0.06 --back_max 30 --num_update_procs 30

end=`date +%s`
runtime=$((end-start))
