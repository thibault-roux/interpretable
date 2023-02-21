import pickle


if __name__ == '__main__':
    # choice = "wer"
    # choice = "bertscore"
    # choice = "bertscore_rescale"
    # choice = "SD_sent_camembase"
    choice = "SD_sent_camemlarge"
    
    if choice == "wer":
        picklename_metric = "wer.pickle"
    elif choice == "bertscore":
        picklename_metric = "bertscore.pickle"
    elif choice == "bertscore_rescale":
        picklename_metric = "bertscore_rescale.pickle"
    elif choice == "SD_sent_camembase":
        picklename_metric = "SD_sent_camembase.pickle"
    elif choice == "SD_sent_camemlarge":
        picklename_metric = "SD_sent_camemlarge.pickle"
    else:
        raise Exception("Unknown choice: ", choice)


    with open(picklename_metric, "rb") as handle:
        save = pickle.load(handle)

    print(type(save))
    for k, v in save.items():
        print("type(k):", type(k))
        print("type(v):", type(v))
        print("k:", k)
        print("len(v):", len(v))
        for minik, miniv in v.items():
            print(type(minik), minik)
            print(type(miniv), miniv)
            input()
        print("----END----")
        input()
