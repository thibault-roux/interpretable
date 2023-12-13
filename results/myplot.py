
import matplotlib.pyplot as plt
import numpy as np

#plt.style.use('_mpl-gallery')


def remove_useless(txt, useless=[" ", "(", ")"]):
    newtxt = ""
    for c in txt:
        if c not in useless:
            newtxt += c
    return float(newtxt)



def plotter(mined, certitude, namefile, adder):
    param = []
    scores = []
    # get data
    with open(namefile, "r", encoding="utf8") as file:
        for LINE in file:
            line = LINE.split(",")
            threshold = float(line[1])
            correct = remove_useless(line[adder+2])
            equal = remove_useless(line[adder+3])
            incorrect = remove_useless(line[adder+4])
            total = correct+equal+incorrect
            
            param.append(threshold)
            scores.append(correct/total*100)
            # by.append(equal/total*100)
            # cy.append(incorrect/total*100)

    # print(param)
    # print(scores)

    # Create a line plot
    plt.plot(param, scores, marker='o', linestyle='-')
    plt.title('Scores vs Parameter Values')
    plt.show()
    plt.xlabel("Threshold")
    plt.ylabel("Percentage")
    # plt.legend()
    plt.savefig("Plots/myplots/min"+mined+str(certitude)+".png")








def process(certitude, mined):
    # automatic setting
    if mined == "wer":
        namefile = "./"
    elif mined == "cer":
        namefile = "./MINCER/"
    else:
        raise Exception("Error, mined:", mined)
    namefile += "SD_sent_camemlarge.txt" # "bertscore_rescale.txt"
    if certitude == 100:
        adder = 0
    elif certitude == 70:
        adder = 3
    else:
        raise Exception("Error, certitude:", certitude)

    plotter(mined, certitude, namefile, adder)





if __name__ == '__main__':
    
    All = False # False

    if not All:
        # parameters to set
        certitude = 100 # ou 70
        mined = "wer" # ou "cer"

        process(certitude, mined)
    else:
        for mined in ["wer", "cer"]:
            print(mined)
            for certitude in [70, 100]:
                print(certitude)
                # automatic setting
                process(certitude, mined)