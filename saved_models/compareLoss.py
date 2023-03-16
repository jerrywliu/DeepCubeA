import matplotlib.pyplot as plt
import numpy as np

from argparse import ArgumentParser

def readLoss(name):
    steps = []
    losses = []

    # Open file to get model output
    with open(f'saved_models/{name}/output.txt') as f:
        for line in f:
            line = line.strip()

            # Get current step size
            if line.startswith("Solving"):
                steps.append(int(line.split()[-2]))
            
            # Get loss
            if line.startswith("Last loss"):
                losses.append(float(line.split()[-1]))
    
    return steps, losses

def main():

    models = [
                "cube2_deepcubea", 
                "cube2_irnext_gamma=1", 
                "cube2_irnext_gamma=large",
                "cube2_irnext_gamma=mid",
            ]
    
    plt.figure(figsize=(15,5))

    for model in models:
        steps, losses = readLoss(model)

                

        iters = np.arange(len(steps))

        steps = np.array(steps)
        losses = np.array(losses)
        maxStep = steps.max()

        plt.plot(iters, losses, label=model)

        # Each step size
        for i in range(1, maxStep+1):
            stepIdxs = np.where(steps == i)

            # If only 1 index point
            #plt.plot(iters[stepIdxs], losses[stepIdxs], 'o', label=f"{i} moves")
    

    # Move plot a bit to the left to make room for legend
    plt.subplots_adjust(left=0.1)
    plt.subplots_adjust(right=0.82)
    # Place legend outside of plot
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title="Scramble Complexity", borderaxespad=0.)

    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.title(f"Training Loss across Gamma Values")

    plt.savefig(f"plots/Compare_Loss_Gamma.png")

if __name__ == "__main__":
    main()
