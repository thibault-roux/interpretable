import aligned_wer as awer

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

def score(sent1, sent2):
    return cosine_similarity(model.encode(sent1).reshape(1, -1), model.encode(sent2).reshape(1, -1))[0][0]



def get_tree(reference, hypothese):
    reference = reference.split(" ")
    hypothese = hypothese.split(" ")
    dico_errors = dict()
    base_errors, dist = awer.wer(reference, hypothese)

    set_errors = set()
    set_errors.add(''.join(base_errors))
    dico_errors[0] = set_errors
    for i in range(1, dist+1):
        set_errors = set()
        for prev_errors in dico_errors[i-1]: # parcours du set (eeieed, eseeed)
            prev_errors = list(prev_errors)
            for j in range(len(prev_errors)):
                new_errors = prev_errors.copy()
                if prev_errors[j] == "s" or prev_errors[j] == "i" or prev_errors[j] == "d":
                    new_errors[j] = "e"
                    set_errors.add(''.join(new_errors))
            dico_errors[i] = set_errors
    return dico_errors, base_errors

def newhyp(errors, new_errors, ref, hyp):
    ref = ref.split(" ")
    hyp = hyp.split(" ")
    errors = list(errors)
    new_errors = list(new_errors)
    
    new_hyp = ""
    i = 0
    i_ref = 0
    i_hyp = 0
    while i < len(errors):
        if errors[i] != new_errors[i]: # correction done on the ith "error"
            corrected = True
        else: # no correction done
            corrected = False
            
        if errors[i] == "e": # already correct
            new_hyp += ref[i_ref] + " "
            i_hyp += 1
            i_ref += 1
        elif errors[i] == "i": # insertion corrected
            if not corrected:
                new_hyp += hyp[i_hyp] + " "
            i_hyp += 1
        elif errors[i] == "d": # deletion corrected
            if corrected:
                new_hyp += ref[i_ref] + " "
            i_ref += 1
        elif errors[i] == "s": # substitution corrected
            if corrected:
                new_hyp += ref[i_ref] + " "
            else:
                new_hyp += hyp[i_hyp] + " "
            i_hyp += 1
            i_ref += 1
        else: 
            print("Error: the newhyp inputs 'errors' and 'new_errors' are expected to be string of e,s,i,d. Received", errors[i])
            exit(-1)
        i += 1
    return new_hyp[:-1]


if __name__ == '__main__':
    reference = "tu manges pas ton kiwi"
    hypothesis = "tu mens je pas ton"

    threshold = 0.93 #if the threshold is equal to the upper limit (1), then minimum WER = WER

    threshold_met = False
    max_score = -9999999

    dico_errors, base_errors = get_tree(reference, hypothesis)
    print(dico_errors)
    #print(''.join(base_errors))
    for k, set_errors in dico_errors.items():
        #print(k, set_errors)
        for e in set_errors:
            new_hypothesis = newhyp(base_errors, e, reference, hypothesis) # new hypothesis partially corrected
            s = score(reference, new_hypothesis)
            print(s, e, new_hypothesis)
            if s >= threshold and s > max_score:
                threshold_met = True
                best_hypothesis = dict()
                best_hypothesis["score"] = s
                best_hypothesis["errors"] = e
                best_hypothesis["hypothesis"] = new_hypothesis
        if threshold_met:
            break
    try:
        minwer = 0
        i = 0
        for c in best_hypothesis["errors"]:
            if c != base_errors[i]:
                print(base_errors[i])
                minwer += 1
            i += 1
        best_hypothesis["minWER"] = minwer
        print(best_hypothesis)
    except NameError:
        print("ERROR: no best_hypothesis found. The threshold is expected to be lower than the upper limit of the score.")
        raise


# ---- for optimization ----
# 1) maybe it would be more pertinent to start from the bottom ?
# 2) the threshold can be obtained from users's perception
# 3) once a value below the threshold is met, stop computation
# 4) no need to compute all of the tree if we start from the top
# 5) if the tree has too many branches, we can applied an heuristic using the performance improvement due to the correction fo an error
#       for example, recover 'kiwi' increase the semdist score from 0.5626 to 0.8387 while delete 'je' decrease the semdist score only from 0.5626 to 0.5014

#miniWER