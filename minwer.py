import aligned_wer as awer

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

def semdist(ref, hyp, memory):
    model = memory
    ref_projection = model.encode(ref).reshape(1, -1)
    hyp_projection = model.encode(hyp).reshape(1, -1)
    score = cosine_similarity(ref_projection, hyp_projection)[0][0]
    return (1-score)*100 # lower is better

def wer(ref, hyp, memory):
    return jiwer.wer(ref, hyp)

def MinWER(ref, hyp, metric, threshold, memory):
    __MAX__ = 10 # maximum distance to avoid too high computational cost
    print(ref)
    print(hyp)
    errors, distance = awer.wer(ref.split(" "), hyp.split(" "))
    base_errors = ''.join(errors)
    level = {''.join(str(x) for x in [0]*distance)}
    # base_errors = ['esieed']
    # distance = 3
    # level = {000}
    if distance <= __MAX__: # to limit the size of graph
        minwer = 0
        while minwer < distance:
            print()
            print(level)
            for node in level:
                print("node:", node)
                corrected_hyp = correcter(ref, hyp, node, base_errors)
                score = metric(ref, corrected_hyp, memory)
                print(str(score) + "\t" + ref + "\t" + corrected_hyp)
                if score < threshold: # lower-is-better
                    return minwer
            level = get_next_level(level)
            minwer += 1
        return distance
    else:
        return distance
        



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


if __name__ == '__main__':
    print("Reading dataset...")
    dataset = read_dataset("hats.txt")


    ref = "I book them an appointment"
    hyp = "book them a appointment and"
    import jiwer
    metric = wer
    threshold = 0.3
    memory = 0
    m = MinWER(ref, hyp, metric, threshold, memory)
    print()
    print("The computed minwer is", m)


