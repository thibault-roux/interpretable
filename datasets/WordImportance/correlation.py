import pickle
from scipy import stats
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity



def get_filenames():
    filenames = []
    with open("wimp_corpus/annotations/annotated_files.txt", "r") as f:
        for line in f:
            filenames.append(line.strip())
    return filenames

def get_annotations(namefile):
    annotations = []
    with open("wimp_corpus/annotations/" + namefile, "r") as f:
        for line in f:
            temp = line.strip().split(" ")
            temp = temp[3:len(temp)]
            temp = [float(x) for x in temp]
            annotations.append(temp)
    return annotations

def get_transcripts(namefile):
    transcripts = []
    with open("swb_ms98_transcriptions/" + namefile, "r") as f:
        for line in f:
            temp = line.strip().split(" ")
            temp = temp[3:len(temp)]
            temp = " ".join(temp)
            transcripts.append(temp)
    return transcripts


def clean_transcript(annotations, transcripts):
    new_annotations = []
    new_transcripts = []
    for i in range(len(annotations)):
        annotation = annotations[i]
        transcript = transcripts[i]
        if "[" not in transcript and "]" not in transcript:
            # remove from transcript the characters between brackets
            new_annotations.append(annotation)
            new_transcripts.append(transcript)
    return new_annotations, new_transcripts



def semdist(ref, hyp, memory):
    model = memory
    ref_projection = model.encode(ref).reshape(1, -1)
    hyp_projection = model.encode(hyp).reshape(1, -1)
    score = cosine_similarity(ref_projection, hyp_projection)[0][0]
    return 1 - score # between 0 and 1 (or more in case of negative score) / lower is better

def remove_word(transcript_list, i):
    hyp = transcript_list[:i] + transcript_list[i+1:]
    return " ".join(hyp)

def compute_scores(sentencebertname):
    filenames = get_filenames()

    sentencemodel = SentenceTransformer(sentencebertname)

    all_metric_scores = dict()
    for namefile in filenames:
        annotations = get_annotations(namefile)
        transcripts = get_transcripts(namefile)
        
        annotations, transcripts = clean_transcript(annotations, transcripts)

        metric_scores = []
        for transcript in transcripts:
            transcript_list = transcript.split(" ")
            for i in range(len(transcript_list)):
                hyp = remove_word(transcript_list, i)
                score = semdist(transcript, hyp, sentencemodel)
                metric_scores.append(score)
        all_metric_scores[namefile] = metric_scores
    sentencebertname = sentencebertname.replace("/", "_")
    with open("pickle/" + sentencebertname + ".pkl", "wb") as f:
        pickle.dump(all_metric_scores, f)


def compute_correlation(sentencebertname, compute_score):

    if compute_score:
        compute_scores(sentencebertname)

    filenames = get_filenames()

    # load pickle
    sentencebertname = sentencebertname.replace("/", "_")
    with open("pickle/" + sentencebertname + ".pkl", "rb") as f:
        all_metric_scores = pickle.load(f)

    err = 0
    corrs = []
    total = 0
    for namefile in filenames:
        annotations = get_annotations(namefile)
        transcripts = get_transcripts(namefile)
        
        annotations, transcripts = clean_transcript(annotations, transcripts)


        # i = 10

        # print(namefile)
        # print(len(annotations), annotations[0], sum([len(x) for x in annotations]))
        # print(len(transcripts), transcripts[0], sum([len(x.split(" ")) for x in transcripts]))
        # alls = all_metric_scores[namefile]
        # print(len(alls), alls[0:len(annotations[0])])


        # annotations : list of 39 lists (total = 623)
        # transcripts : list of 39 strings (total = 623)
        # all_metric_scores[namefile] : list of 623 floats
        # exit()

        prev = 0
        for i in range(len(annotations)):
            # len(annotations[i]) = 1..30 # différentes valeurs possibles
            # print("len(annotations[i]):", len(annotations[i]))
            next = prev + len(annotations[i])
            if len(annotations[i]) > -1 and len(annotations[i]) < 100000:
                # print("prev:", prev, "next:", next)
                corr = stats.spearmanr(all_metric_scores[namefile][prev:next], annotations[i])
                total += len(all_metric_scores[namefile])
                sd_scores = all_metric_scores[namefile][prev:next]
                # for iterator in range(len(sd_scores)):
                #     sd_scores[iterator] = 1/(1+2.718**(-sd_scores[iterator]*10))
                #     sd_scores[iterator] = round(sd_scores[iterator], 2)
                # print(sd_scores)
                # print(annotations[i])
                # print(transcripts[i])
                # print(corr[0])
                # print()

                # [0.51, 0.56, 0.51] / [0.0033661723136901855, 0.024717211723327637, 0.0022231340408325195]
                # [0.0, 0.1, 0.3]
                # well that's nice
                # input()
                if corr[0] != corr[0]:
                    err += 1
                    # if len(annotations[i]) > 1:
                    #     print(len(annotations[i]))
                else:
                    corrs.append(corr[0])
            prev = next
    print("len(corrs):", len(corrs))
    print("total:", total)
    print(sum(corrs)/len(corrs))
    exit()


if __name__ == "__main__":
    sentencebertname = ["dangvantuan/sentence-camembert-large", "paraphrase-MiniLM-L6-v2", "all-mpnet-base-v2", "multi-qa-mpnet-base-dot-v1", "all-distilroberta-v1", "all-MiniLM-L12-v2", "paraphrase-MiniLM-L3-v2"]
    for s in sentencebertname:
        print("start: ", s)
        compute_correlation(s, compute_score=False)
        print("done: ", s)
        print()