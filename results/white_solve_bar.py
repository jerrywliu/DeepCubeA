import pickle
import numpy as np
import matplotlib.pyplot as plt


def white_percent(color, cube):
    if (cube == "cube2"):
        skip = 2
    elif (cube == "cube3"):
        skip = 1

    score = 0
    for i in range(0, 9, skip):
        if color[i] == i:
            score += 1
    
    maxScore = 9
    if (cube == "cube2"):
        score -= 1 # ignore center
        maxScore = 4 # only corners

    return score / maxScore

def calculate_average(all_scores, name):
    # Get longest trajectory
    max_len = 0
    for scores in all_scores:
        if len(scores) > max_len:
            max_len = len(scores)

    # Get average score for all trajectories
    overall_average = 0
    for scores in all_scores:
        overall_average += np.mean(scores)
    overall_average /= len(all_scores)

    # find std deviation of average score
    overall_std = 0
    for scores in all_scores:
        overall_std += (np.mean(scores) - overall_average)**2
    overall_std /= len(all_scores)
    overall_std = np.sqrt(overall_std)

    return overall_average, overall_std

def open_trajectory(result_dir, name):
    with open(result_dir + "results.pkl", 'rb') as f:
        result = pickle.load(f)

    trajs = []

    # Get all 100 trajectories
    trajs.append([
        [state.colors for state in traj]
        for traj in result["paths"]
    ])

    avgs = []
    all_scores = []

    for traj in trajs[-1]:
        scores = []
        for color in traj:
            score = white_percent(color, "cube2")
            scores.append(score)
        
        all_scores.append(scores)

    return calculate_average(all_scores, name)

if __name__ == "__main__":
    
    # Files to check
    # TODO: Add the irnext_gamma=large file when done training
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

    plt.figure(figsize=(10,5))
    avgs = []
    stds = []

    for dir,name in zip(dirs, names):
        avg, std = open_trajectory(dir,name)
        avgs.append(avg)
        stds.append(std)

    print(avgs)
    print(stds)
    plt.bar(range(len(names)), avgs, yerr=[stds,stds], tick_label=names, color='#ff7f0e')
    
    plt.title("Cube2: Average % that white face is complete over entire solve trajectory")
    plt.ylabel("Percent of white layer complete")
    plt.savefig("plots/cube2_white_percent_bar.png")

