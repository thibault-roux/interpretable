import aligned_wer as awer
from flair.data import Sentence
from flair.models import SequenceTagger
import progressbar

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
        elif errors[i] == "i": # insertion corrected
            if corrected[INDEX] == '0': # if we do not correct the error
                new_hyp += hyp[ih] + " " # the extra word is not deleted
            ih += 1
            INDEX += 1
            # print("i\t", new_hyp)
        elif errors[i] == "d": # deletion
            if corrected[INDEX] == '1': # if we do correct the error
                new_hyp += ref[ir] + " " # we add the missing word
            ir += 1
            INDEX += 1
        elif errors[i] == "s": # substitution
            if corrected[INDEX] == '1':
                new_hyp += ref[ir] + " "
            else:
                new_hyp += hyp[ih] + " " # we do not correct the substitution 
            ih += 1
            ir += 1
            INDEX += 1
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


def pos_analyze(ref, hyp, posref, metric, dicopos, mapper, memory):
    errors, distance = awer.wer(ref.split(" "), hyp.split(" "))
    previous_score = metric(ref, hyp, memory)
    base_errors = ''.join(errors)
    level = {''.join(str(x) for x in [0]*distance)}
    level = get_next_level(level)
    gains = dict()
    for node in level:
        corrected_hyp = correcter(ref, hyp, node, base_errors)
        score = metric(ref, corrected_hyp, memory)
        gains[node] = int((previous_score - score)*10000)/100
        # save score and compare

    
    refsplit = ref.split(" ")
    ir = 0
    inode = 0 # useless for now
    gainid = [0]*distance
    for i in range(len(errors)):
        error = errors[i]
        if error == "s" or error == "d":
            pos = posref[ir] # get pos from reference
            gain = gains[get_index(inode, gainid)]
            try:
                dicopos[pos].append(gain)
            except KeyError:
                print(pos)
                print(dicopos)
                raise
            ir += 1
            inode += 1
        elif error == "e":
            ir += 1
        elif error == "i":
            gain = gains[get_index(inode, gainid)]
            dicopos["<ins>"].append(gain)
            inode += 1
        else:
            raise Exception("Unexpected error: " + error)
    # ref: salut tu vas bien
    # err:   D       S         I
    # hyp:       tu va  bien hein


"""
def semdist(ref, hyp, memory):
    model = memory
    ref_projection = model.encode(ref).reshape(1, -1)
    hyp_projection = model.encode(hyp).reshape(1, -1)
    score = cosine_similarity(ref_projection, hyp_projection)[0][0]
    return (1-score) # lower is better
"""

def wer(ref, hyp, memory):
    return jiwer.wer(ref, hyp)

def cer(ref, hyp, memory):
    return jiwer.cer(ref, hyp)

def get_index(inode, gainid):
    gainid = gainid.copy()
    gainid[inode] = 1
    return ''.join(str(e) for e in gainid)


if __name__ == '__main__':

    """
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    print("Loading model...")
    model = SentenceTransformer('dangvantuan/sentence-camembert-large')
    print("Model loaded.")
    memory = model
    metric = semdist
    """
    import jiwer
    memory = 0
    metric = cer #wer

    
    # Load the model
    model = SequenceTagger.load("qanastek/pos-french")
    # Load mapper
    mapper = dict()
    POS = set()
    with open("datasets/mapping.txt", "r", encoding="utf8") as file:
        for Line in file:
            line = Line[:-1].split("\t")
            mapper[line[0]] = line[1]
            POS.add(line[1])
    POS.add("<ins>")
    # dict[pos] = gain
    dicopos = dict()
    for pos in POS:
        dicopos[pos] = []


    bar = progressbar.ProgressBar(max_value=2000)
    iterator_progressbar = 0
    with open("datasets/hats.txt", "r", encoding="utf8") as file:
        next(file)
        for Line in file:
            line = line.split("\t")
            ref = line[0]
            for ind in [1, 3]:
                hyp = line[ind] # A or B
                # get POS
                sentence = Sentence(ref)
                model.predict(sentence)   
                posref = list(mapper[c[1:-1]] for i, c in enumerate(sentence.to_tagged_string().split(" ")) if (i+1)%2 == 0) # just get POS from the tagger instead of word & pos
                # get gain from pos
                pos_analyze(ref, hyp, posref, metric, dicopos, mapper, memory)
                iterator_progressbar += 1
                bar.update(iterator_progressbar)

    print(dicopos)

    
