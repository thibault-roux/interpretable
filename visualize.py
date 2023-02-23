import aligned_wer as awer

# We want to visualize word gravity

# how ?
# we know that some corrections implies better gains


def add_eps_ref(ref, errors):
    ref = ref.split(" ")
    newref = ""
    ir = 0
    for i in range(len(errors)):
        error = errors[i]
        if error == "i":
            newref += bcolors.RED + "ε" + bcolors.ENDC + " "
        elif error == "e":
            newref += bcolors.BLUE + ref[ir] + bcolors.ENDC + " "
            ir += 1
        elif error == "s" or error == "d":
            newref += bcolors.RED + ref[ir] + bcolors.ENDC + " "
            ir += 1
        else:
            raise Exception("Unexpected error: " + error)
    return newref[:-1]

def add_eps_hyp(hyp, errors):
    hyp = hyp.split(" ")
    newhyp = ""
    ih = 0
    for i in range(len(errors)):
        error = errors[i]
        if error == "d":
            newhyp += bcolors.RED + "ε" + bcolors.ENDC + " "
        elif error == "e":
            newhyp += bcolors.BLUE + hyp[ih] + bcolors.ENDC + " "
            ih += 1
        elif error == "s" or error == "i":
            newhyp += bcolors.RED + hyp[ih] + bcolors.ENDC + " "
            ih += 1
        else:
            raise Exception("Unexpected error: " + error)
    return newhyp[:-1]


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


def semdist(ref, hyp, memory):
    model = memory
    ref_projection = model.encode(ref).reshape(1, -1)
    hyp_projection = model.encode(hyp).reshape(1, -1)
    score = cosine_similarity(ref_projection, hyp_projection)[0][0]
    return (1-score) # lower is better

def wer(ref, hyp, memory):
    return jiwer.wer(ref, hyp)

def get_index(inode, gainid):
    #gainid = gainid.copy()
    print(inode, gainid)
    gainid[inode] = 1
    return ''.join(str(e) for e in gainid)

if __name__ == '__main__':
    # ref = input("Reference: ")
    # hyp = input("Hypothesis: ")
    ref = "salut ça va mon beau"
    hyp = "salut va toi mon beau"

    # find word with error. Insert a token for deletion?

    errors, distance = awer.wer(ref.split(" "), hyp.split(" "))

    """
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    model = SentenceTransformer('dangvantuan/sentence-camembert-large')
    memory = model
    metric = semdist
    """
    import jiwer
    memory = 0
    metric = wer

    previous_score = metric(ref, hyp, memory)
    base_errors = ''.join(errors)
    level = {''.join(str(x) for x in [0]*distance)}
    level = get_next_level(level)
    gains = dict()
    for node in level:
        print("node = ", node)
        corrected_hyp = correcter(ref, hyp, node, base_errors)
        score = metric(ref, corrected_hyp, memory)
        gains[node] = previous_score - score
        # save score and compare
    
    print("gains = ", gains)

    # print
    hyp = hyp.split(" ")
    newhyp = ""
    ih = 0
    inode = 0
    gainid = [0]*distance
    for i in range(len(errors)):
        error = errors[i]
        if error == "d":
            newhyp += bcolors.RED + "ε" + bcolors.ENDC + "("+str(gains[get_index(inode, gainid)])+")" + " "
        elif error == "e":
            newhyp += bcolors.BLUE + hyp[ih] + bcolors.ENDC + " "
            ih += 1
        elif error == "s" or error == "i":
            newhyp += bcolors.RED + hyp[ih] + bcolors.ENDC + "("+str(gains[get_index(inode, gainid)])+")" + " "
            ih += 1
        else:
            raise Exception("Unexpected error: " + error)
    print(newhyp)

    # we do not want all possibilities from a level
    # we just want the possibilities given one
    
