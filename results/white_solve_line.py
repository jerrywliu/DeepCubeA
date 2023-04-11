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

def plot_scores(all_scores, name):
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
    print(name, "overall_average:", overall_average)
    
    # Pad all trajectories to be the same length
    for i in range(len(all_scores)):
        while len(all_scores[i]) < max_len:
            all_scores[i].append(1)

    
    # Convert to numpy array
    all_scores = np.array(all_scores)

    """All of these are with the 1 padding at the end (if solve trajectory is shorter than max_len)"""
    # Get max score for each timestep
    max_scores = np.max(all_scores, axis=0)
    # Get min score for each timestep
    min_scores = np.min(all_scores, axis=0)
    # Get average score for each timestep
    average_scores = np.mean(all_scores, axis=0)

    # Plot
    plt.plot(np.arange(max_len), average_scores, alpha=0.8, label=name)

    # TODO: If we want to plot the min and max scores, uncomment this
    #plt.fill_between(np.arange(max_len), min_scores, max_scores, alpha=0.3)

def open_trajectory(result_dir, name, mode):
    with open(result_dir + "results.pkl", 'rb') as f:
        result = pickle.load(f)

    trajs = []

    # Get all 100 trajectories
    trajs.append([
        [state.colors for state in traj]
        for traj in result["paths"][1:2]
    ])

    all_scores = []

    for traj in trajs[-1]:
        scores = []
        for color in traj:
            score = white_percent(color, mode)
            scores.append(score)
        
        all_scores.append(scores)

    plot_scores(all_scores, name)

if __name__ == "__main__":
    
    # Files to check
    # TODO: Add the irnext_gamma=large file when done training
    # dirs = [
    #     "results/cube2_deepcubea/",
    #     "results/cube2_irnext_gamma=mid/",
    #     "results/cube2_irnext_gamma=large/",
    #     "results/cube2_irnext_gamma=1/"
    # ]

    # names = [
    #     "DCA (gamma=0)",
    #     "DCA-LBL-gamma=0.5",
    #     "DCA-LBL-gamma=0.9",
    #     "DCA-LBL-gamma=1"
    # ]

    dirs = [
        "results/cube3/",
        "results/cube3_intermediate_reward/",
    ]

    names = [
        "DCA (gamma=0)",
        "DCA-LBL-gamma=0.9",
    ]

    mode = "cube3"

    plt.figure(figsize=(10,5))
    for dir,name in zip(dirs, names):
        open_trajectory(dir, name, mode)
    plt.legend()
    plt.title(f"Cube3: % of white layer solved during each timestep")
    plt.xlabel("Solve Timestep")
    plt.ylabel("Percent of white layer solved")
    plt.savefig(f"plots/{mode}_white_line.png")

