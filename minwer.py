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
            if error != 0:
                new_errors = errors.copy()
                new_errors[i] = 1
                level.add(''.join(new_errors)) # add list (converted to string)
    return level

def correcter(ref, hyp, corrected, base_errors):
    # ref, hyp, corrected (100), base_errors (deesei)
    errors = list(errors) # convert string to list
    # deesei
    # 000
    # return hyp

    # 100 # INDEX   corrected[INDEX] = True or False ?
    # for e in errors:
    # if e == "s":
    INDEX = 0

    new_hyp = ""
    ir = 0
    ih = 0
    for i in range(len(errors)):
        if errors[i] == "e": # already
            print("e\t'" + ref[ir] + "' issu de la référence.")
            new_hyp += ref[ir] + " "
            ih += 1
            ir += 1
            print("\t", new_hyp)
        elif errors[i] == "i": # insertion
            if corrected[INDEX] = 
            print("i\t'" + hyp[ih] + "' issu de l'hypothèse.")
            new_hyp += hyp[ih] + " "
            ih += 1
            print("\t", new_hyp)
        elif errors[i] == "d": # deletion
            print("d\t'" + ref[ir] + "' est ignoré.")
            #new_hyp += ref[ir] + " "
            ir += 1
            print("\t", new_hyp)
        elif errors[i] == "s": # substitution
            print("s\t'" + hyp[ih] + "' est issu de l'hypothèse.")
            new_hyp += hyp[ih] + " "
            ih += 1
            ir += 1
            print("\t", new_hyp)
        else: 
            print("Error: the newhyp inputs 'errors' and 'new_errors' are expected to be string of e,s,i,d. Received", errors[i])
            exit(-1)
        i += 1
    input()
    return new_hyp[:-1]

def semdist(ref, hyp, memory):
    model = memory
    ref_projection = model.encode(ref).reshape(1, -1)
    hyp_projection = model.encode(hyp).reshape(1, -1)
    score = cosine_similarity(ref_projection, hyp_projection)[0][0]
    return (1-score)*100 # lower is better

def minwer(ref, hyp, metric, memory):
    __MAX__ = 10 # maximum distance to avoid too high computational cost
    ref = ref.split(" ")
    hyp = hyp.split(" ")

    print(ref)
    print(hyp)
    errors, distance = awer.wer(ref, hyp)
    base_errors = ''.join(errors)
    level = [0]*distance
    # base_errors = ['esieed']
    # distance = 3
    # level = [0, 0, 0]
    if distance <= __MAX__: # to limit the size of graph
        print(level)
        for l in level:
            print(l)
            print("\t", correcter(ref, hyp, l, base_errors))
        level = get_next_level(level)
        print(level)
        for l in level:
            print(l)
            print("\t", correcter(ref, hyp, l, base_errors))
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


def edit_distance(ref, hyp):
    return wer(ref, hyp)*len(ref.split(" "))

if __name__ == '__main__':
    print("Reading dataset...")
    dataset = read_dataset("hats.txt")


    minwer("I book them an appointment", "book them a appointment and", 0, 0)


