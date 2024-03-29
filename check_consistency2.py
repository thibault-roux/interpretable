import progressbar
import aligned_wer as awer
import numpy
import pickle

# problem: in a previous version, the computation of graph can be very expensive, without considering the metric cost
# with 40 errors (which happens), we have 10^12 nodes.

# instead, we would like to compute to compute only the next level

# for scores, I should store them in a file with 'ref \t hyp \t score \n', store them in a set and rewrite the file every time




def get_next_level(prev_level):
    # Will compute all possibilities for the next level of the graph.

    # INPUT: 
    #   prev_level = {001, 010, 000}
    # OUTPUT: 
    #   level == {101, 011, 110}

    level = set()
    for errors in prev_level:
        errors = list(errors) # string to list for item assigment
        for i in range(len(errors)):
            error = errors[i]
            if error == '0':
                new_errors = errors.copy()
                new_errors[i] = 1
                level.add(''.join(str(x) for x in new_errors)) # add list (converted to string)
    return level

def correcter(ref, hyp, corrected, errors):
    # ref, hyp, corrected (100), errors (deesei)

    ref = ref.split(" ")
    hyp = hyp.split(" ")
    INDEX = 0

    new_hyp = ""
    ir = 0
    ih = 0
    for i in range(len(errors)):
        if errors[i] == "e": # already
            new_hyp += ref[ir] + " "
            ih += 1
            ir += 1
            # print("e\t", new_hyp)
        elif errors[i] == "i": # insertion corrected
            if corrected[INDEX] == '0': # if we do not correct the error
                new_hyp += hyp[ih] + " " # the extra word is not deleted
            ih += 1
            INDEX += 1
            # print("i\t", new_hyp)
        elif errors[i] == "d": # deletion
            if corrected[INDEX] == '1': # if we do correct the error
                new_hyp += ref[ir] + " " # we add the missing word
            # else  # we do not restaure the missing word
            ir += 1
            INDEX += 1
            # print("d\t", new_hyp)
        elif errors[i] == "s": # substitution
            if corrected[INDEX] == '1':
                new_hyp += ref[ir] + " "
            else:
                new_hyp += hyp[ih] + " " # we do not correct the substitution 
            ih += 1
            ir += 1
            INDEX += 1
            # print("s\t", new_hyp)
        else: 
            print("Error: the newhyp inputs 'errors' and 'new_errors' are expected to be string of e,s,i,d. Received", errors[i])
            exit(-1)
        i += 1
    return new_hyp[:-1]

def bertscore(ref, hyp, memory):
    scorer = memory
    P, R, F1 = scorer.score([hyp], [ref])
    return 1-F1

def semdist(ref, hyp, memory):
    model = memory
    ref_projection = model.encode(ref).reshape(1, -1)
    hyp_projection = model.encode(hyp).reshape(1, -1)
    score = cosine_similarity(ref_projection, hyp_projection)[0][0]
    return (1-score) # lower is better

def wer(ref, hyp, memory):
    return jiwer.wer(ref, hyp)

def MinWER1(ref, hyp, metric, threshold, save, memory):
    __MAX__ = 10 # maximum distance to avoid too high computational cost
    errors, distance = awer.wer(ref.split(" "), hyp.split(" "))
    base_errors = ''.join(errors)
    level = {''.join(str(x) for x in [0]*distance)}
    # base_errors = ['esieed']
    # distance = 3
    # level = {000}
    if distance <= __MAX__: # to limit the size of graph
        minwer = 0
        while minwer < distance:
            for node in level:
                corrected_hyp = correcter(ref, hyp, node, base_errors)
                # optimization to avoid recomputation
                try:
                    score = save[ref][corrected_hyp]
                except KeyError:
                    score = metric(ref, corrected_hyp, memory)
                    if ref not in save:
                        save[ref] = dict()
                    save[ref][corrected_hyp] = score
                if score < threshold: # lower-is-better
                    return minwer
            level = get_next_level(level)
            minwer += 1
        return distance
    else:
        return distance


def MinWER2(ref, hyp, metric, threshold, save, memory):
    errors, distance = awer.wer(ref.split(" "), hyp.split(" "))
    base_errors = ''.join(errors)
    level = {''.join(str(x) for x in [0]*distance)}

    # base_errors = ['esieed']
    # distance = 3
    # level = {000}

    scores = dict()
    try:
        base_score = save[ref][hyp]
    except KeyError:
        base_score = metric(ref, hyp, memory)
        if ref not in save:
            save[ref] = dict()
        save[ref][hyp] = base_score
    
    level = get_next_level(level)
    for node in level:
        corrected_hyp = correcter(ref, hyp, node, base_errors)
        # optimization to avoid recomputation
        try:
            score = save[ref][corrected_hyp]
        except KeyError:
            score = metric(ref, corrected_hyp, memory)
            if ref not in save:
                save[ref] = dict()
            save[ref][corrected_hyp] = score
        scores[node] = score
    scores_array = list(scores.values())
    improvements_array = [base_score - score for score in scores_array]

    minwer = 0
    corrected_score = base_score
    while corrected_score > threshold and minwer < distance:
        max_improvement = max(improvements_array)
        
        corrected_score = corrected_score - max_improvement
        improvements_array.remove(max_improvement)
        minwer += 1
    return minwer
        



def read_dataset(dataname):
    # dataset = [{"reference": ref, "hypA": hypA, "nbrA": nbrA, "hypB": hypB, "nbrB": nbrB}, ...]
    dataset = []
    with open("datasets/" + dataname, "r", encoding="utf8") as file:
        next(file)
        for line in file:
            line = line[:-1].split("\t")
            dictionary = dict()
            dictionary["reference"] = line[0]
            dictionary["hypA"] = line[1]
            dictionary["nbrA"] = int(line[2])
            dictionary["hypB"] = line[3]
            dictionary["nbrB"] = int(line[4])
            dataset.append(dictionary)
    return dataset

def checker(metric, dataset, threshold, memory, picklename_metric, verbose=True):
    differents = 0
    total = 0

    # recover scores save
    try:
        with open(picklename_metric, "rb") as handle:
            save = pickle.load(handle)
    except FileNotFoundError:
        save = dict()

    if verbose:
        bar = progressbar.ProgressBar(max_value=len(dataset))
    for i in range(len(dataset)):
        if verbose:
            bar.update(i)
        
        scoreA1 = MinWER1(dataset[i]["reference"], dataset[i]["hypA"], metric, threshold, save, memory)
        scoreA2 = MinWER2(dataset[i]["reference"], dataset[i]["hypA"], metric, threshold, save, memory)
        if scoreA1 != scoreA2:
            differents += 1
        total += 1

        scoreB1 = MinWER1(dataset[i]["reference"], dataset[i]["hypB"], metric, threshold, save, memory)
        scoreB2 = MinWER2(dataset[i]["reference"], dataset[i]["hypB"], metric, threshold, save, memory)
        if scoreB1 != scoreB2:
            differents += 1
        total += 1


    print()
    print("Differents:", differents, "/", total, "=", differents/total)

        
    # storing scores save
    with open(picklename_metric, "wb") as handle:
        pickle.dump(save, handle, protocol=pickle.HIGHEST_PROTOCOL)






if __name__ == '__main__':
    print("Reading dataset...")
    dataset = read_dataset("hats.txt")

    # choice = "wer"
    # choice = "bertscore"
    # choice = "bertscore_rescale"
    # choice = "SD_sent_camembase"
    choice = "SD_sent_camemlarge"
    

    if choice == "wer":
        import jiwer
        memory = 0
        metric = wer
        picklename_metric = "pickle/wer.pickle"
    elif choice == "bertscore":
        from bert_score import BERTScorer
        memory = BERTScorer(lang="fr")
        metric = bertscore
        picklename_metric = "pickle/bertscore.pickle"
    elif choice == "bertscore_rescale":
        from bert_score import BERTScorer
        memory = BERTScorer(lang="fr", rescale_with_baseline=True)
        metric = bertscore
        picklename_metric = "pickle/bertscore_rescale.pickle"
    elif choice == "SD_sent_camembase":
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        model = SentenceTransformer('dangvantuan/sentence-camembert-base')
        memory = model
        metric = semdist
        picklename_metric = "pickle/SD_sent_camembase.pickle"
    elif choice == "SD_sent_camemlarge":
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        model = SentenceTransformer('dangvantuan/sentence-camembert-large')
        memory = model
        metric = semdist
        picklename_metric = "pickle/SD_sent_camemlarge.pickle"
    else:
        raise Exception("Unknown choice: ", choice)
    
    print()
    

    threshold = 0.024
    # picklename_metric = "pickle/temp.pickle"
    checker(metric, dataset, threshold, memory, picklename_metric)
