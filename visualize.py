

# We want to visualize word gravity

# how ?
# we know that some corrections implies better gains




if __name__ == '__main__':
    ref = input("Reference: ")
    hyp = input("Hypothesis: ")

    # find word with error. Insert a token for deletion?

    errors, distance = awer.wer(ref.split(" "), hyp.split(" "))