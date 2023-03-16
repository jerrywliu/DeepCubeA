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

    labels = [
        "cube2_DCA_gamma=0",
        "cube2_LBL_gamma=1",
        "cube2_LBL_gamma=0.9",
        "cube2_LBL_gamma=0.5",
    ]

    for i, model in enumerate(models):
        steps, losses = readLoss(model)

                

        iters = np.arange(len(steps))

        steps = np.array(steps)
        losses = np.array(losses)
        maxStep = steps.max()

        plt.plot(iters, losses, label=labels[i])


    plt.legend(loc="upper right")

    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.title(f"Training Loss across Gamma Values")

    plt.savefig(f"plots/Compare_Loss_Gamma.png")

if __name__ == "__main__":
    main()
