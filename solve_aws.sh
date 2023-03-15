#!/bin/bash
rm -rf ~/.cache/torch_extensions

start=`date +%s`

set -ex

python3 search_methods/astar.py --language cpp --states data/cube3/test/data_0.pkl --model saved_models/cube3/current/ --env cube3 --weight 0.6 --batch_size 1 --nnet_batch_size 1 --results_dir results/cube3_intermediate_reward/

end=`date +%s`
runtime=$((end-start))
