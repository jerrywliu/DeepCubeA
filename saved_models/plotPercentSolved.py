import matplotlib.pyplot as plt
import numpy as np

from argparse import ArgumentParser

def parse_arguments(parser):
    parser.add_argument('--model', type=str, default="cube2_deepcubea", help="Folder name in saved_models")
    return vars(parser.parse_args())

def processBackstep(line, epoch):
    line = line.split()
    # backstep
    backstep = line[2]
    backstep = int(backstep[:-1])

    # solved percent
    percent = line[4]
    percent = float(percent[:-1])

    return backstep, percent

def main():
    parser = ArgumentParser()
    args = parse_arguments(parser)

    backstep_2d = []
    epochs = 0

    # Open file to get model output
    with open(f'saved_models/{args["model"]}/output.txt') as f:
        for line in f:
            line = line.strip()

            # Get current step size
            if line.startswith("Test time:"):
                epochs += 1
            
            # Get loss
            if line.startswith("Back Steps:"):
                backstep, percentSolved = processBackstep(line, epochs)
                if (backstep == 0):
                    backstep_2d.append([])
                else:
                    backstep_2d[epochs].append(percentSolved)

    maxBackstep = len(backstep_2d[0])
    epochIterator = np.arange(epochs)

    backstep_2d_np = np.array(backstep_2d)
    backstep_2d_np = backstep_2d_np.T

    plt.figure(figsize=(15,5))

    for i in range(1, maxBackstep, 1):
        plt.plot(epochIterator, backstep_2d_np[i], label=f"{i} moves")

    # Move plot a bit to the left to make room for legend
    plt.subplots_adjust(left=0.1)
    plt.subplots_adjust(right=0.82)
    # Place legend outside of plot
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title="Scramble Complexity", borderaxespad=0.)
    plt.xlabel("Epochs")
    plt.ylabel("% of Cubes Solved")
    plt.title(f"% of Cubes Solved during Training for {args['model']}")

    plt.savefig(f"plots/[%_SOLVED]{args['model']}.png")

if __name__ == "__main__":
    main()
