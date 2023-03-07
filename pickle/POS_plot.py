import pickle
import numpy as np
import matplotlib.pyplot as plt

# add a plotter using the dico of pos for gains
# dicopos[pos] = [0.30, 20, -1, 39]

# use the pickle file "posgain.pickle"

with open("posgain.pickle", "rb") as handle:
    dicopos = pickle.load(handle)

print(len(dicopos))
print(dicopos.keys())

fig, ax = plt.subplots()

iterator_position = 0
x_pos = []
x_values = []
# for pos, gains in dicopos.items():
for pos in sorted(dicopos.keys()):
    gains = dicopos[pos]
    if len(gains) > 0:
        print(pos, len(gains), sum(gains)/len(gains))
        iterator_position += 3
        x_pos.append(pos)
        x_values.append(iterator_position)
        x = (np.random.rand(1, len(gains))-0.5)*2 + iterator_position

        # ax.scatter(x, gains, s=10, c='blue', label=pos, alpha=0.4) #, edgecolors='black')
        ax.scatter(x, gains, s=1, label=pos, alpha=0.7) #, edgecolors='black')
        
        """lgnd = ax.legend(loc = "lower center", bbox_to_anchor = (1, 0.5))
        for i in range(len(lgnd.legendHandles)):
            lgnd.legendHandles[i]._sizes = [30]"""

        plt.xticks(x_values, x_pos, fontsize=6)
        ax.set(ylim=(-20, 20))
        # ax.set(xlim=(0, len(x)), ylim=(0, 1.1)) # xticks=np.arange(0, 0.25, 0.05),
        #    ylim=(40, 100), yticks=np.arange(40, 101, 10))"""

        

        plt.show()
        plt.savefig("plot_POS.png")






    else:
        print(pos, "empty.")

# plt.scatter()