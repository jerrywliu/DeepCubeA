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

def open_trajectory(result_dir):
    with open(result_dir + "results.pkl", 'rb') as f:
        result = pickle.load(f)

    trajs = []

    # Get all 100 trajectories
    trajs.append([
        [state.colors for state in traj]
        for traj in result["paths"]
    ])

    print("result_dir: ", result_dir)

    avg_scores = np.array([])

    for traj in trajs[-1]:
        scores = []
        for color in traj:
            score = white_percent(color, "cube2")
            scores.append(score)
        
        average_score = sum(scores) / len(scores)
        
        scores_list = np.append(scores_list, average_score)

    print("white score", scores_list.mean())


if __name__ == "__main__":
    
    # Files to check
    # TODO: Add the irnext_gamma=large file when done training
    dirs = [
        "results/cube2_deepcubea/",
        "results/cube2_irnext_gamma=mid/",
        "results/cube2_irnext_gamma=1/"
        #"cube2_irnext_gamma=large"
    ]

    for dir in dirs:
        open_trajectory(dir)

