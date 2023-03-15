import pickle

with open("results/cube3/results.pkl", 'rb') as f:
    data = pickle.load(f)

#print(data["paths"][0][0].colors)
print(data["solutions"][0])
