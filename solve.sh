#!/bin/bash
#SBATCH -c 20
#SBATCH --gres=gpu:2
#SBATCH --partition=compsci-gpu

rm -rf ~/.cache/torch_extensions

start=`date +%s`

set -ex

python3 search_methods/astar.py --states data/cube3/test/data_0.pkl --model saved_models/cube3/current/ --env cube3 --weight 0.6 --batch_size 10 --results_dir results/cube3_intermediate_reward/ --language cpp --nnet_batch_size 100 --end_idx 10

end=`date +%s`
runtime=$((end-start))
