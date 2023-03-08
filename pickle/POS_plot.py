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

x_errorbar = []
y_errorbar = []
yerr = []

# for pos, gains in dicopos.items():
for pos in sorted(dicopos.keys()):
    gains = dicopos[pos]
    if len(gains) > 0:
        themean = sum(gains)/len(gains)
        print(pos, len(gains), themean)
        iterator_position += 3
        x_pos.append(pos)
        x_values.append(iterator_position)
        x = (np.random.rand(1, len(gains))-0.5)*3 + iterator_position

        ax.scatter(x, gains, s=15, label=pos, alpha=1)
        
        # error bar
        x_errorbar.append(iterator_position)
        y_errorbar.append(themean)
        yerr.append(np.std(gains)/2)
    else:
        print(pos, "empty.")

ax.errorbar(x_errorbar, y_errorbar, yerr, c='black', fmt='o', markersize=6, linewidth=1.75, capsize=5, alpha=1)
plt.xticks(x_values, x_pos, rotation=30, fontsize=9)
ax.set(ylim=(-15, 25))
ax.tick_params(labelright=True)

print(fig.get_size_inches())
fig.set_size_inches(6.4, 4.8)

plt.show()
plt.savefig("plot_POS.png", dpi=300)