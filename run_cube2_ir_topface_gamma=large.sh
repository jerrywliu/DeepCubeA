#!/bin/bash
#SBATCH -c 40
#SBATCH --gres=gpu:4
#SBATCH --partition=compsci-gpu
#SBATCH --nodelist=gpu-compute4

rm -rf ~/.cache/torch_extensions

start=`date +%s`

set -ex

python3 ctg_approx/avi.py --env cube2 --states_per_update 5000000 --batch_size 1000 --nnet_name cube2_ir_topface_gamma=large --max_itrs 350000 --loss_thresh 0.06 --back_max 15 --num_update_procs 39 --inter_reward ir_topface

end=`date +%s`
runtime=$((end-start))
