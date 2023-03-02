import pickle
from jiwer import wer, cer
import numpy as np

# this code is expected to display in one plot the sorted scores (by CER?) of WER, CER and another embedding-based metric (SemDist?)
# these scores are computed on the HATS dataset, between the reference and each hypothesis






def semdist(ref, hyp, memory):
    model = memory
    ref_projection = model.encode(ref).reshape(1, -1)
    hyp_projection = model.encode(hyp).reshape(1, -1)
    score = cosine_similarity(ref_projection, hyp_projection)[0][0]
    return (1-score) # lower is better






if __name__ == '__main__':

    refs = []
    hyps = []
    with open("hats.txt", "r", encoding="utf8") as file:
        for LINE in file:
            line = LINE.split("\t")
            refs.append(line[0])
            hyps.append((line[1], line[3]))



    # choice = "wer"
    # choice = "bertscore"
    # choice = "bertscore_rescale"
    # choice = "SD_sent_camembase"
    choice = "SD_sent_camemlarge"
    
    if choice == "wer":
        picklename_metric = "wer.pickle"
    elif choice == "bertscore":
        picklename_metric = "bertscore.pickle"
    elif choice == "bertscore_rescale":
        picklename_metric = "bertscore_rescale.pickle"
    elif choice == "SD_sent_camembase":
        picklename_metric = "SD_sent_camembase.pickle"
    elif choice == "SD_sent_camemlarge":
        picklename_metric = "SD_sent_camemlarge.pickle"
    else:
        raise Exception("Unknown choice: ", choice)

    with open("../pickle/" + picklename_metric, "rb") as handle:
        save = pickle.load(handle)

    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    model = SentenceTransformer('dangvantuan/sentence-camembert-large')
    memory = model
    metric = semdist



    wers = []
    cers = []
    embs = [] # metric embedding-based
    for i in range(len(refs)):
        for hyp in hyps[i]:
            wers.append(wer(refs[i], hyp))
            cers.append(cer(refs[i], hyp))
            try:
                embs.append(save[refs[i]][hyp]) # metric(refs[i], hyp))
            except KeyError:
                print("Not found in pickle.")
                embs.append(metric(refs[i], hyp, memory))

    """
    print(embs)

    wers = np.array(wers)
    cers = np.array(cers)
    embs = np.array(embs)

    print(embs)
    """

    x = np.arange(0, len(wers), 1)
    args = np.argsort(cers)
    wers = wers[args]
    cers = cers[args]
    embs = embs[args]
    y = np.vstack([wers, cers, embs])

    fig, ax = plt.subplots()

    ax.stackplot(x, y)


    """ax.set(xlim=(0, 0.25), xticks=np.arange(0, 0.25, 0.05),
        ylim=(40, 100), yticks=np.arange(40, 101, 10))"""

    plt.show()
    plt.savefig("plot.png")