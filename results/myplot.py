import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

#plt.style.use('_mpl-gallery')


def remove_useless(txt, useless=[" ", "(", ")"]):
    newtxt = ""
    for c in txt:
        if c not in useless:
            newtxt += c
    return float(newtxt)



def get_scores(mined, certitude, namefile, adder):
    if mined == "wer":
        param = [0]
        scores = [63.07]
    elif mined == "cer":
        param = [0]
        scores = [76.55]
    else:
        raise Exception("Error, mined:", mined)
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
    return param, scores


def obtain_data(certitude, mined):
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

    param, scores = get_scores(mined, certitude, namefile, adder)
    return param, scores




def plotter(param1, scores1, param2, scores2):

    sns.set(style="whitegrid")

    plt.axhline(y=89.75, linestyle='-', color=sns.color_palette("muted")[2])
    plt.axhline(y=63.07, linestyle='-', color=sns.color_palette("muted")[3])
    plt.axhline(y=76.55, linestyle='-', color=sns.color_palette("muted")[4])

    # Create a line plot
    plt.plot(param1, scores1, marker='o', linestyle='-', markersize=5, color=sns.color_palette("muted")[0])
    plt.plot(param2, scores2, marker='o', linestyle='-', markersize=5, color=sns.color_palette("muted")[1])
    plt.title('Scores vs Parameter Values')
    plt.show()
    plt.xlabel("Threshold")
    plt.ylabel("Percentage")
    # plt.legend()
    plt.savefig("Plots/myplots/bestplot.png")






if __name__ == '__main__':
    
    certitude = 100
    
    mined = "wer"
    param1, scores1 = obtain_data(certitude, mined)
    mined = "cer"
    param2, scores2 = obtain_data(certitude, mined)
    
    plotter(param1, scores1, param2, scores2)