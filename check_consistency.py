import progressbar
import aligned_wer as awer
import numpy
import pickle

# problem: in a previous version, the computation of graph can be very expensive, without considering the metric cost
# with 40 errors (which happens), we have 10^12 nodes.

# instead, we would like to compute to compute only the next level

# for scores, I should store them in a file with 'ref \t hyp \t score \n', store them in a set and rewrite the file every time



# DONE - 1) compute the number of errors in the dataset
# 2) compute the partial graph when computations is too excessive
# 3) reformulate the problem with boolean vector



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
    return 1-F1.item()

def semdist(ref, hyp, memory):
    model = memory
    ref_projection = model.encode(ref).reshape(1, -1)
    hyp_projection = model.encode(hyp).reshape(1, -1)
    score = cosine_similarity(ref_projection, hyp_projection)[0][0]
    return (1-score) # lower is better

def wer(ref, hyp, memory):
    return jiwer.wer(ref, hyp)

def MinWER(ref, hyp, metric, save, memory):
    __MAX__ = 10 # maximum distance to avoid too high computational cost
    errors, distance = awer.wer(ref.split(" "), hyp.split(" "))
    base_errors = ''.join(errors)
    level = {''.join(str(x) for x in [0]*distance)}
    # base_errors = ['esieed']
    # distance = 3
    # level = {000}     1: {00}     2: {01, 10}     3: {11}

    # dict[modif] = [gain1, gain2]
    # store previous score
    if distance <= __MAX__: # to limit the size of graph
        minwer = 0

        # 101
        # 111
        # I should store all scores in a dico of dico == dico[level][modif] = score

        ALL_scores = dict()
        for d in range(distance+1):
            ALL_scores[d] = dict()

        while minwer <= distance:
            # compare 000 et 100, 010, 001 (on peut faire un genre de soustraction)
            # problem: at the first step, there is no previous level
            # we should compute a score between the ref and hypothesis (not corrected) outside of the while
            
            #print("LEVEL :", minwer)
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
                # print("\t", corrected_hyp, score)
                ALL_scores[minwer][node] = score
            
            # print(ALL_scores)
            level = get_next_level(level)
            minwer += 1

        gains = dict()
        for i in range(distance):
            gains[i] = []
        """print(gains)
        print(ALL_scores)
        print(len(ALL_scores))"""
        for minwer, dico1 in ALL_scores.items():
            if minwer+1 < len(ALL_scores):
                dico2 = ALL_scores[minwer+1]
                for node2, score2 in dico2.items(): # node == modif == 001
                    for node1, score1 in dico1.items():
                        child, m = is_child(node1, node2)
                        if child: # is_child()
                            gain = score2 - score1
                            gains[m].append(gain)

                            """print("It is a child!")
                            corrected_hyp1 = correcter(ref, hyp, node1, base_errors)
                            corrected_hyp2 = correcter(ref, hyp, node2, base_errors)
                            print(corrected_hyp1)
                            print(corrected_hyp2)
                            print(gain)"""
            # print(minwer)
        # ce que je veux:
        # une liste des gains d'une modification
        # pour chaque modification possible
        #print(gains)
        #input()
        
        return gains # ALL_scores
    else:
        return None # TO RESOLVE AS IT IS NOT A LIST

def is_child(node1, node2):
    """print("\nis_child()")
    print(node1)
    print(type(node1))
    print(node2)
    print(type(node2))"""

    node1 = list(int(c) for c in node1)
    node2 = list(int(c) for c in node2)
    zero = 0
    one = 0
    for i in range(len(node1)):
        val = node2[i] - node1[i]
        if val == 0:
            zero += 1
        elif val == 1:
            one += 1
            index = i
        else:
            return False, -999
    if zero == len(node1)-1 and one == 1:
        return True, index
    else:
        raise("Unexpected error. Check node1 and node2:\n" + str(node1) + "\n" + str(node2))



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

def evaluator(metric, dataset, memory, picklename_metric, picklegains, verbose=True):
    # recover scores save
    try:
        with open(picklename_metric, "rb") as handle:
            save = pickle.load(handle)
    except FileNotFoundError:
        save = dict()

    total_gain = []
    if verbose:
        bar = progressbar.ProgressBar(max_value=len(dataset))
    for i in range(len(dataset)):
        if verbose:
            bar.update(i)
        nbrA = dataset[i]["nbrA"]
        nbrB = dataset[i]["nbrB"]
        
        gains1 = MinWER(dataset[i]["reference"], dataset[i]["hypA"], metric, save, memory)
        gains2 = MinWER(dataset[i]["reference"], dataset[i]["hypB"], metric, save, memory)

        if gains1 is not None:
            for k, gains in gains1.items():
                total_gain.append(gains)
        if gains2 is not None:
            for k, gains in gains2.items():
                total_gain.append(gains)
    
    with open(picklegains, "wb") as handle:
        pickle.dump(total_gain, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # compute average of standard deviations for each gains
    print("Computing average of standard deviations for each gains...")
    stds = []
    max_diff = []
    for gains in total_gain:
        stds.append(numpy.std(gains))
        max_diff.append(max(gains)-min(gains))
    print(stds)
    avg_std = sum(stds)/len(stds) # average of standard deviation
    avg_max_diff = sum(max_diff)/len(max_diff)
    print("Average of standard deviation:", avg_std)
    print("Average of max difference:", avg_max_diff)

    # storing scores save
    with open(picklename_metric, "wb") as handle:
        pickle.dump(save, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return avg_std

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
        picklegains = "pickle/wer_total_gain.pickle"
    elif choice == "bertscore":
        from bert_score import BERTScorer
        memory = BERTScorer(lang="fr")
        metric = bertscore
        picklename_metric = "pickle/bertscore.pickle"
        picklegains = "pickle/bertscore_total_gain.pickle"
    elif choice == "bertscore_rescale":
        from bert_score import BERTScorer
        memory = BERTScorer(lang="fr", rescale_with_baseline=True)
        metric = bertscore
        picklename_metric = "pickle/bertscore_rescale.pickle"
        picklegains = "pickle/bertscore_rescale_total_gain.pickle"
    elif choice == "SD_sent_camembase":
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        model = SentenceTransformer('dangvantuan/sentence-camembert-base')
        memory = model
        metric = semdist
        picklename_metric = "pickle/SD_sent_camembase.pickle"
        picklegains = "pickle/SD_sent_camembase_total_gain.pickle"
    elif choice == "SD_sent_camemlarge":
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        model = SentenceTransformer('dangvantuan/sentence-camembert-large')
        memory = model
        metric = semdist
        picklename_metric = "pickle/SD_sent_camemlarge.pickle"
        picklegains = "pickle/SD_sent_camemlarge_total_gain.pickle"
    else:
        raise Exception("Unknown choice: ", choice)
    
    print()
    evaluator(metric, dataset, memory, picklename_metric, picklegains, verbose=True)

