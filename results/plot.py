
import matplotlib.pyplot as plt
import numpy as np

#plt.style.use('_mpl-gallery')


def remove_useless(txt, useless=[" ", "(", ")"]):
    newtxt = ""
    for c in txt:
        if c not in useless:
            newtxt += c
    return float(newtxt)



def plotter(mined, certitude, namefile):
    x = []
    ay = []
    by = []
    cy = []

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

    ax.set(xlim=(0, 0.25), xticks=np.arange(0, 0.25, 0.05),
        ylim=(40, 100), yticks=np.arange(40, 101, 10))

    plt.show()
    plt.savefig("Plots/min"+mined+str(certitude)+".png")








if __name__ == '__main__':
    
    All = True # False

    if not All:
        # parameters to set
        certitude = 70 # ou 70
        mined = "cer" # ou "cer"

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

        plotter(mined, certitude, namefile)

    for mined in ["wer", "cer"]:
        for certitude in [70, 100]:
            print(certitude)
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

            plotter(mined, certitude, namefile)
            plotter(mined, certitude, namefile)