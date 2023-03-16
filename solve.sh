#!/bin/bash
#SBATCH -c 20
#SBATCH --gres=gpu:2
#SBATCH --partition=compsci-gpu

rm -rf ~/.cache/torch_extensions

start=`date +%s`

set -ex

python3 search_methods/astar.py --states data/cube3/test/data_0.pkl --model saved_models/cube2_irnext_gamma=mid/current --env cube2 --weight 0.6 --batch_size 1 --results_dir results/cube2_irnext_gamma=mid/ --language cpp --nnet_batch_size 1 --end_idx 100

end=`date +%s`
runtime=$((end-start))
