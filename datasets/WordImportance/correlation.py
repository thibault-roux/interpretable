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
    with open(sentencebertname + ".pkl", "wb") as f:
        pickle.dump(all_metric_scores, f)

        


if __name__ == "__main__":
    sentencebertname = 'dangvantuan/sentence-camembert-large'

    # compute_scores(sentencebertname)

    filenames = get_filenames()

    # load pickle
    sentencebertname = sentencebertname.replace("/", "_")
    with open(sentencebertname + ".pkl", "rb") as f:
        all_metric_scores = pickle.load(f)

    err = 0
    corrs = []
    for namefile in filenames:
        annotations = get_annotations(namefile)
        transcripts = get_transcripts(namefile)
        
        annotations, transcripts = clean_transcript(annotations, transcripts)

        
        prev = 0
        for i in range(len(annotations)):
            next = prev + len(annotations[i])
            corr = stats.spearmanr(all_metric_scores[namefile][prev:next], annotations[i])
            prev = next
            if corr[0] != corr[0]:
                err += 1
                # if len(annotations[i]) > 1:
                #     print(len(annotations[i]))
            else:
                corrs.append(corr[0])
    print("err: ", err)
    print("len(corrs): ", len(corrs))
    print(sum(corrs)/len(corrs))