import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import sys
from tqdm import tqdm

COLOR_MAP = np.array([
    [255, 255, 255], # white
    [0, 255, 0], # green
    [255, 0, 0], # red
    [0, 0, 255], # blue
    [255, 165, 0], # orange
    [255, 255, 0], # yellow
])

def plot(traj, sample_id, result_path):
    fig, axes = plt.subplots(nrows=3, ncols=4, sharex=True, sharey=True)
    fig.set_facecolor("grey")
    for x in axes:
        for y in x:
            y.axis("off")
    plt.subplots_adjust(wspace=0, hspace=0)
    
    for k in range(len(traj[sample_id])):
        axes[0, 1].imshow(COLOR_MAP[traj[sample_id][k][0]])
        axes[1, 0].imshow(COLOR_MAP[traj[sample_id][k][1]])
        axes[1, 1].imshow(COLOR_MAP[traj[sample_id][k][2]])
        axes[1, 2].imshow(COLOR_MAP[traj[sample_id][k][3]])
        axes[1, 3].imshow(COLOR_MAP[traj[sample_id][k][4]])
        axes[2, 1].imshow(COLOR_MAP[traj[sample_id][k][5]])

        save_dir = result_path + "sample_traj/{}".format(sample_id)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        fig.savefig(save_dir + "/{}.png".format(k))

def main(result0_path, result1_path, num_samples=10):
    with open(result0_path + "results.pkl", 'rb') as f:
        result0 = pickle.load(f)
    with open(result1_path + "results.pkl", "rb") as f:
        result1 = pickle.load(f)

    steps = []
    trajs = []
    times = []
    num_nodes = []

    for result in [result0, result1]:
        steps.append(result["solutions"][:num_samples])
        trajs.append([
            [state.colors for state in traj]
            for traj in result["paths"][:num_samples]
        ])
        times.append(result["times"][:num_samples])
        num_nodes.append(result["num_nodes_generated"][:num_samples])

        # convert indexed colors to color map
        for traj in trajs[-1]:
            for colors in traj:
                for i in range(len(colors)):
                    if colors[i] < 9: # white
                        colors[i] = 0
                    elif colors[i] < 18: # green
                        colors[i] = 1
                    elif colors[i] < 27: # red
                        colors[i] = 2
                    elif colors[i] < 36: # blue
                        colors[i] = 3
                    elif colors[i] < 45: # orange
                        colors[i] = 4
                    else: # yellow
                        colors[i] = 5
            for j in range(len(traj)):
                traj[j] = np.reshape(traj[j], (6, 3, 3))
    
    for traj, result_path in zip(trajs, [result0_path, result1_path]):
        for sample_idx in tqdm(range(len(traj))):
            plot(traj, sample_idx, result_path)

if __name__ == "__main__":
    if len(sys.argv) != 4 and len(sys.argv) != 1:
        print("Usage:")
        print("  python dechk_results.py <result0 pickle path> \
<result1 pickle path> <number of samples to check>")

    if len(sys.argv) == 4:
        result0_path = str(sys.argv[1])
        result1_path = str(sys.argv[2])
        num_samples = int(sys.argv[3])
    else:
        result0_path = str("results/cube3/")
        result1_path = str("results/cube3_intermediate_reward/")
        num_samples = 10
    
    main(result0_path, result1_path, num_samples)