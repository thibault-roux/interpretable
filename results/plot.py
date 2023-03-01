
import matplotlib.pyplot as plt
import numpy as np

#plt.style.use('_mpl-gallery')

# make data
x = np.arange(0, 10, 2)
ay = [1, 1.25, 2, 2.75, 3]
by = [1, 1, 1, 1, 1]
cy = [2, 1, 2, 1, 2]


# parameters to set
certitude = 100 # ou 70
mined = "wer" # ou "cer"

# automatic setting
if mined == "wer":
    namefile = "./"
elif mined == "cer":
    namefile = "./MINCER/"
else:
    raise Exception("Error, mined:", mined)
namefile += "SD_sentcamemlarge.txt"
if certitude == 100:
    adder = 0
elif certitude == 70:
    adder = 3
else:
    raise Exception("Error, certitude:", certitude)

# get data
with open(namefile, "r", encoding="utf8") as file:
    for LINE in file:
        line = LINE.split(",")
        threshold = line[1]



y = np.vstack([ay, by, cy])

# plot
fig, ax = plt.subplots()

ax.stackplot(x, y)

ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
       ylim=(0, 8), yticks=np.arange(1, 8))

plt.show()
plt.savefig("Plots/plot.png")