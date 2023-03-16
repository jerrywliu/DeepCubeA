import matplotlib.pyplot as plt
import numpy as np

from argparse import ArgumentParser

def parse_arguments(parser):
    parser.add_argument('--model', type=str, default="cube2_deepcubea", help="Folder name in saved_models")
    return vars(parser.parse_args())

def main():
    parser = ArgumentParser()
    args = parse_arguments(parser)

    steps = []
    losses = []

    # Open file to get model output
    with open(f'saved_models/{args["model"]}/output.txt') as f:
        for line in f:
            line = line.strip()

            # Get current step size
            if line.startswith("Solving"):
                steps.append(int(line.split()[-2]))
            
            # Get loss
            if line.startswith("Last loss"):
                losses.append(float(line.split()[-1]))
                

    iters = np.arange(len(steps))

    steps = np.array(steps)
    losses = np.array(losses)
    maxStep = steps.max()

    plt.figure(figsize=(15,5))
    # Each step size
    for i in range(1, maxStep+1):
        stepIdxs = np.where(steps == i)

        # If only 1 index point
        if (len(stepIdxs[0]) == 1):
            plt.plot(iters[stepIdxs], losses[stepIdxs], '-o', label=f"{i} moves")
        else:
            plt.plot(iters[stepIdxs], losses[stepIdxs], label=f"{i} moves")

    # Move plot a bit to the left to make room for legend
    plt.subplots_adjust(left=0.1)
    plt.subplots_adjust(right=0.82)
    # Place legend outside of plot
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title="Scramble Complexity", borderaxespad=0.)

    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.title(f"Training Loss and Cube Complexity for {args['model']}")

    plt.savefig(f"plots/[LOSS]{args['model']}.png")

if __name__ == "__main__":
    main()
