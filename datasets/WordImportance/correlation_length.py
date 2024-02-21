import pickle
from scipy import stats
import jiwer



# metrics

def cer(ref, hyp, memory=None, i=None):
    return jiwer.cer(ref, hyp) # lower is better, i.e the longer is the word, the higher is the score

def length_of_word(ref, hyp, memory, i): # compute the importance of the missing word in a sentence
    ref = ref.split(" ")
    return len(ref[i])

def frequency(ref, hyp, memory, i):
    wrd2freq, total = memory
    ref = ref.split(" ")
    wrd = ref[i]
    return wrd2freq[wrd]/total

    



# ---------------

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


def remove_word(transcript_list, i):
    hyp = transcript_list[:i] + transcript_list[i+1:]
    return " ".join(hyp)


def compute_scores(metricname, metric, memory=None):
    filenames = get_filenames()


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
                score = metric(transcript, hyp, memory, i)
                metric_scores.append(score)
        all_metric_scores[namefile] = metric_scores
    with open("pickle/" + metricname + ".pkl", "wb") as f:
        pickle.dump(all_metric_scores, f)


def compute_correlation(metricname, metric, compute_score):


    filenames = get_filenames()

    if compute_score:
        if metricname == "cer":
            memory = None
        elif metricname == "wer":
            memory = None
        elif metricname[:4] == "bert":
            # modelname = 'camembert-base'
            modelname = metricname[5:]
            bert, log = AutoModel.from_pretrained(modelname, output_loading_info=True)
            bert_tokenizer = AutoTokenizer.from_pretrained(modelname, do_lowercase=True)
            memory=(bert_tokenizer, bert)
        elif metricname == "phoner":
            # phoner
            lang_code = 'fra-Latn-p'
            memory = epitran.Epitran(lang_code)
        elif metricname == "length_of_word":
            memory = None
        elif metricname == "frequency":
            wrd2freq = dict()
            total = 0
            for namefile in filenames:
                transcripts = get_transcripts(namefile)
                for transcript in transcripts:
                    transcript_list = transcript.split(" ")
                    for i in range(len(transcript_list)):
                        total += 1
                        wrd = transcript_list[i]
                        if wrd not in wrd2freq:
                            wrd2freq[wrd] = 1
                        wrd2freq[wrd] += 1
            memory = (wrd2freq, total)

        compute_scores(metricname, metric, memory)


    # load pickle
    with open("pickle/" + metricname + ".pkl", "rb") as f:
        all_metric_scores = pickle.load(f)

    err = 0
    corrs = []
    total = 0
    dicorrs = dict()
    for i in range(30):
        dicorrs[i] = []
    for namefile in filenames:
        annotations = get_annotations(namefile)
        transcripts = get_transcripts(namefile)
        
        annotations, transcripts = clean_transcript(annotations, transcripts)

        prev = 0
        for i in range(len(annotations)):
            total += 1
            next = prev + len(annotations[i])
            # to avoid weird cases
            # if True
            if len(annotations[i]) > 3: # and len(annotations[i]) < 10:
                # compute correlation
                corr = stats.pearsonr(all_metric_scores[namefile][prev:next], annotations[i])
                # print(all_metric_scores[namefile][prev:next])
                # print(annotations[i])
                # print()

                # to avoid nan values
                if corr[0] != corr[0]:
                    err += 1
                else:
                    corrs.append(corr[0])
                    if len(annotations[i]) not in dicorrs:
                        dicorrs[len(annotations[i])] = []
                    dicorrs[len(annotations[i])].append(corr[0])
            prev = next
    print("len(corrs):", len(corrs))
    print("total:", total)
    print("err:", err)
    print("ratio accepted:", len(corrs)/(total-err))
    # average of correlation per length of annotations
    # for k, v in dicorrs.items():
    #     if len(v) > 0:
    #         print(k, len(v), round(sum(v)/len(v), 3))
    # average of correlation
    print(sum(corrs)/len(corrs))


if __name__ == "__main__":
    metricnames = ["cer", "frequency"]
    metrics = [cer, frequency]
    for i in range(len(metricnames)):
        metricname = metricnames[i]
        metric = metrics[i]
        print("start: ", metricname)
        compute_correlation(metricname, metric, compute_score=True)
        print("done: ", metricname)
        print()