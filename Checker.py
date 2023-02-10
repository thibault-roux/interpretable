import numpy
import pickle



if __name__ == '__main__':
    with open("pickle/total_gain.pickle", "rb") as handle:
        total_gain = pickle.load(handle)

    # compute average of standard deviations for each gains
    print("Computing average of standard deviations for each gains...")
    stds = []
    nbr = 0
    for gains in total_gain:
        if len(gains) > 10:
            std = numpy.std(gains)
            stds.append(std)
            nbr += 1
    print(nbr)
    #print(stds)
    avg_std = sum(stds)/len(stds) # average of standard deviation
    print("Average of standard deviation:", avg_std)

    # instead of average of standard deviations, I could simply compute the maximum difference with the
    # first gain or with the average.