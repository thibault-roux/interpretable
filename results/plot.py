
import matplotlib.pyplot as plt
import numpy as np

#plt.style.use('_mpl-gallery')


def remove_useless(txt, useless=[" ", "(", ")"]):
    newtxt = ""
    for c in txt:
        if c not in useless:
            newtxt += c
    return float(newtxt)


x = []
ay = []
by = []
cy = []

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
namefile += "SD_sent_camemlarge.txt"
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
        threshold = float(line[1])
        correct = remove_useless(line[adder+2])
        equal = remove_useless(line[adder+3])
        incorrect = remove_useless(line[adder+4])
        total = correct+equal+incorrect
        
        x.append(threshold)
        ay.append(correct/total*100)
        by.append(equal/total*100)
        cy.append(incorrect/total*100)

x = np.array(x)
ay = np.array(ay)
by = np.array(by)
cy = np.array(cy)
args = np.argsort(x)

x = x[args]
ay = ay[args]
by = by[args]
cy = cy[args]

y = np.vstack([ay, by, cy])

# plot
fig, ax = plt.subplots()

ax.stackplot(x, y)

#ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
#       ylim=(0, 8), yticks=np.arange(1, 8))

plt.show()
plt.savefig("Plots/min"+mined+str(certitude)+".png")