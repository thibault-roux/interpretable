import pickle
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
    hyp = transcript[:i] + transcript[i+1:]
    return " ".join(hyp)

if __name__ == "__main__":
    filenames = get_filenames()

    sentencemodel = SentenceTransformer('dangvantuan/sentence-camembert-large')

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
                score = semdist(transcript, hyp, model)
                metric_scores.append(score)
        all_metric_scores[namefile] = metric_scores
    with open("metrics.pkl", "wb") as f:
        pickle.dump(all_metric_scores, f)

        
