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
# plt.axhline(y=0, linestyle='--', markevery=1, linewidth=1, color='black', alpha=1)
# plt.grid(True, axis='y')

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

        # ax.scatter(x, gains, s=10, c='blue', label=pos, alpha=0.4) #, edgecolors='black')
        ax.scatter(x, gains, s=15, label=pos, alpha=1) #, edgecolors='black')
        # ax.scatter([iterator_position], [themean], s=5, c="black")
        
        # error bar
        x_errorbar.append(iterator_position)
        y_errorbar.append(themean)
        yerr.append(np.std(gains)/2)
    else:
        print(pos, "empty.")
"""lgnd = ax.legend(loc = "lower center", bbox_to_anchor = (1, 0.5))
for i in range(len(lgnd.legendHandles)):
    lgnd.legendHandles[i]._sizes = [30]"""

ax.errorbar(x_errorbar, y_errorbar, yerr, c='black', fmt='o', markersize=6, linewidth=1.75, capsize=5, alpha=1)
plt.xticks(x_values, x_pos, rotation=90, fontsize=9)
ax.set(ylim=(-15, 25))
ax.tick_params(labelright=True)
# ax.set(xlim=(0, len(x)), ylim=(0, 1.1)) # xticks=np.arange(0, 0.25, 0.05),
#    ylim=(40, 100), yticks=np.arange(40, 101, 10))"""

"""fig_size = plt.rcParams["figure.figsize"] #Get current size
print("Current size:", fig_size)
fig_size[0] = 39
plt.rcParams["figure.figsize"] = fig_size
fig_size = plt.rcParams["figure.figsize"] #Get current size
print("Current size:", fig_size)"""

#plt.figure(figsize=(,60), dpi=80)
print(fig.get_size_inches())
fig.set_size_inches(6.4, 4.8)

plt.show()
plt.savefig("plot_POS.png", dpi=300)
# plt.scatter()