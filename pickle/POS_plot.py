import pickle
# import matplotlib.pyplot as plt

# add a plotter using the dico of pos for gains
# dicopos[pos] = [0.30, 20, -1, 39]

# use the pickle file "posgain.pickle"

with open("posgain.pickle", "rb") as handle:
    dicopos = pickle.load(handle)

print(len(dicopos))
print(dicopos.keys())
for k, v in dicopos.items():
    try:
        print(k, sum(v)/len(v))
    except ZeroDivisionError:
        print(k, "empty.")

# plt.scatter()