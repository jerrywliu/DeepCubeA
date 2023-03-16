from glob import glob
import matplotlib
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import sys
from tqdm import tqdm

COLOR_MAP = np.array([
    [255, 255, 255], # white
    [255, 255, 0], # yellow
    [0, 0, 255], # blue
    [0, 255, 0], # green
    [255, 165, 0], # orange
    [255, 0, 0], # red
])
FLOWCHART_WIDTH = 8
MAP = np.array([8, 5, 2, 7, 4, 1, 6, 3, 0, 35, 32, 29, 34, 31, 28, 33, 30, 27, 53, 50, 47, 52, 49, 46, 51, 48, 45, 26, 23, 20, 25, 22, 19, 24, 21, 18, 44, 41, 38, 43, 40, 37, 42, 39, 36, 17, 14, 11, 16, 13, 10, 15, 12, 9])


def plot(traj, sample_id, result_path):
    fig, axes = plt.subplots(nrows=3, ncols=4, sharex=True, sharey=True)
    fig.set_facecolor("grey")
    #fig.set_dpi(100)
    for x in axes:
        for y in x:
            y.axis("off")
    plt.subplots_adjust(wspace=0, hspace=0)
    
    for k in range(len(traj[sample_id])):
        axes[0, 1].imshow(COLOR_MAP[traj[sample_id][k][0]])
        axes[1, 0].imshow(COLOR_MAP[traj[sample_id][k][1]])
        axes[1, 1].imshow(COLOR_MAP[traj[sample_id][k][2]])
        axes[1, 2].imshow(COLOR_MAP[traj[sample_id][k][3]]) # WARNING: changed 
        axes[1, 3].imshow(COLOR_MAP[traj[sample_id][k][4]]) # WARNING: changed
        axes[2, 1].imshow(COLOR_MAP[traj[sample_id][k][5]])

        save_dir = result_path + "sample_traj/{}/".format(sample_id)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        fig.savefig(save_dir + "{}.png".format(k))
        plt.close()


def combine_imgs(result_path, idx, traj_len):
    load_dir = result_path + "sample_traj/{}/".format(idx)
    height = int((traj_len - 1) / FLOWCHART_WIDTH) + 1
    
    fig, axes = plt.subplots(nrows=height, ncols=FLOWCHART_WIDTH, sharex=True, sharey=True)
    fig.set_facecolor("grey")
    fig.set_dpi(600)
    fig.set_size_inches(8, 3)
    for x in axes:
        for y in x:
            y.axis("off")
    plt.subplots_adjust(wspace=0, hspace=0)

    for i in range(height):
        for j in range(FLOWCHART_WIDTH):
            state_idx = i*FLOWCHART_WIDTH + j
            if state_idx >= traj_len:
                break
            path = load_dir + "{}.png".format(state_idx)

            img = mpimg.imread(path)
            axes[i, j].imshow(img)

    save_path = result_path + "sample_traj/full_{}.png".format(idx)
    fig.savefig(save_path)
    plt.close()

def make_trajectory_plot(result0_path, result1_path, num_samples=10):
    with open(result0_path + "results.pkl", 'rb') as f:
        result0 = pickle.load(f)
    with open(result1_path + "results.pkl", "rb") as f:
        result1 = pickle.load(f)

    steps = []
    trajs = []

    for result in [result0, result1]:
        steps.append(result["solutions"][:num_samples])
        trajs.append([
            [state.colors for state in traj]
            for traj in result["paths"][:num_samples]
        ])

        # convert indexed colors to color map
        for traj in trajs[-1]:
            for colors in traj:
                for i in range(len(colors)):
                    if colors[i] < 9: # white
                        colors[i] = 0
                    elif colors[i] < 18: # yellow
                        colors[i] = 1
                    elif colors[i] < 27: # blue
                        colors[i] = 2
                    elif colors[i] < 36: # green
                        colors[i] = 3
                    elif colors[i] < 45: # orange
                        colors[i] = 4
                    else: # red
                        colors[i] = 5
            for j in range(len(traj)):
                traj[j] = np.reshape(traj[j][MAP], (6, 3, 3))
                #traj[j] = np.transpose(traj[j], axes=(0, 2, 1))
    
    for traj, result_path in zip(trajs, [result0_path, result1_path]):
        for sample_idx in tqdm(range(len(traj))):
            plot(traj, sample_idx, result_path)
            # Combine images generated
            combine_imgs(result_path, sample_idx, len(traj[sample_idx]))


def make_time_plot(result0_path, result1_path, num_samples=10):
    with open(result0_path + "results.pkl", 'rb') as f:
        result0 = pickle.load(f)
    with open(result1_path + "results.pkl", "rb") as f:
        result1 = pickle.load(f)
    
    times = []
    
    for result in [result0, result1]:
        times.append(result["times"][:num_samples])
    
    mean0 = np.mean(times[0])
    mean1 = np.mean(times[1])
    std0 = np.std(times[0])
    std1 = np.std(times[1])
    
    plt.bar([0, 1], [mean0, mean1],
            tick_label=["DCA", "DCA-IR"],
            yerr=[[std0, std1], [std0, std1]])
    plt.title("Time A*-solve takes using DCA and DCA-IR")
    plt.savefig("plots/cube3_DCA_vs_DCA-IR_time.png")


def make_node_plot(result0_path, result1_path, num_samples=10):
    with open(result0_path + "results.pkl", 'rb') as f:
        result0 = pickle.load(f)
    with open(result1_path + "results.pkl", "rb") as f:
        result1 = pickle.load(f)
    
    num_nodes = []
    
    for result in [result0, result1]:
        num_nodes.append(result["num_nodes_generated"][:num_samples])

    mean0 = np.mean(num_nodes[0])
    mean1 = np.mean(num_nodes[1])
    std0 = np.std(num_nodes[0])
    std1 = np.std(num_nodes[1])
    
    plt.bar([0, 1], [mean0, mean1],
            tick_label=["DCA", "DCA-IR"],
            yerr=[[std0, std1], [std0, std1]])
    plt.title("Nodes explored during A*-solve using DCA and DCA-IR")
    plt.savefig("plots/cube3_DCA_vs_DCA-IR_node.png")


def main(result0_path, result1_path, num_samples=10, task="all"):
    if task == "all" or task == "trajectory_plot":
        make_trajectory_plot(result0_path, result1_path, num_samples)
    if task == "all" or task == "other_plots":
        make_time_plot(result0_path, result1_path, num_samples)
        make_node_plot(result0_path, result1_path, num_samples)


if __name__ == "__main__":
    if len(sys.argv) != 5 and len(sys.argv) != 1:
        print("Usage:")
        print("  python dechk_results.py <result0 pickle path> \
<result1 pickle path> <number of samples to check> <trajectory_plot/other_plots>")

    if len(sys.argv) == 4:
        result0_path = str(sys.argv[1])
        result1_path = str(sys.argv[2])
        num_samples = int(sys.argv[3])
        task = str(sys.argv[4])
    else:
        result0_path = str("results/cube3/")
        result1_path = str("results/cube3_intermediate_reward/")
        num_samples = 10
        task = "other_plots" #"all"
    
    main(result0_path, result1_path, num_samples, task)
