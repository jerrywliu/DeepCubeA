import matplotlib.pyplot as plt
import numpy as np
import pickle


colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

def make_time_plot(dirs, names, mode):
    bars = range(len(dirs))

    means = []
    stds = []

    for dir in dirs:
        with open(dir + "results.pkl", "rb") as f:
            result = pickle.load(f)

        times = result["times"]

        means.append(np.mean(times))
        stds.append(np.std(times))
    
    plt.figure(figsize=(10,5))
    plt.bar(bars, means, tick_label=names, yerr=[stds,stds], color=colors)
    plt.title(f"{mode}: Time A*-solve takes to solve the cube across gamma values")
    plt.savefig(f"plots/{mode}_time_gamma_sweep.png")


def make_node_plot(dirs, names, mode):
    bar_range = range(len(dirs))

    means = []
    medians = []
    stds = []

    # the four basic plt colors

    # hist plot
    for dir, name, color in zip(dirs, names, colors):
        with open(dir + "results.pkl", "rb") as f:
            result = pickle.load(f)

        arr = result["num_nodes_generated"]

        # remove outliers, values over 4000
        arr = [x for x in arr if x < 1000000]

        print(f"{name}: {len(arr)}")
        print("max", max(arr))


        mean = np.mean(arr)
        medians = np.median(arr)
        std = np.std(arr)
        means.append(mean)
        stds.append(std)

        plt.figure()
        plt.hist(arr, bins=50, color=color, label=name)
        plt.ylabel("Frequency")
        plt.xlabel("Number of nodes explored")
        plt.title(f"{mode}: Mean nodes explored in 100 trajectories")
        plt.legend()
        plt.savefig(f"plots/{mode}_{name}_nodes_explored_hist.png")
        

    # means plot
    plt.figure(figsize=(10,5))
    plt.bar(bar_range, means, tick_label=names, alpha = 0.7, color='blue', label="Mean")
    plt.bar(bar_range, medians, tick_label=names, alpha = 0.7, color='red', label="Median")
    plt.title(f"{mode}: Nodes explored during A*-solve across different gamma values")
    plt.legend()
    plt.savefig(f"plots/{mode}_node_gamma_sweep.png")




def make_step_plot(dirs, names, mode):

    bar_range = range(len(dirs))

    means = []
    stds = []

    for dir, name, color in zip(dirs, names, colors):
        with open(dir + "results.pkl", "rb") as f:
            result = pickle.load(f)
        
        steps = result["solutions"]
        mean = np.mean([len(step) for step in steps])
        std = np.std([len(step) for step in steps])
        
        means.append(mean)
        stds.append(std)
    
    plt.figure(figsize=(10,5))
    plt.bar(bar_range, means, tick_label=names, yerr=[stds,stds], color=colors, label=name)
    plt.title(f"{mode}: Steps taken during A*-solve using across different gamma values")
    plt.savefig(f"plots/{mode}_step_gamma_sweep.png")


def bars(dirs, names, mode):
    make_node_plot(dirs, names, mode)
    make_step_plot(dirs, names, mode)
    make_time_plot(dirs, names, mode)

if __name__ == "__main__":
    dirs = [
        "results/cube2_deepcubea/",
        "results/cube2_irnext_gamma=mid/",
        "results/cube2_irnext_gamma=large/",
        "results/cube2_irnext_gamma=1/"
    ]

    names = [
        "DCA (gamma=0)",
        "DCA-LBL-gamma=0.5",
        "DCA-LBL-gamma=0.9",
        "DCA-LBL-gamma=1"
    ]

    mode = "Cube2" 

    bars(dirs, names, mode)
