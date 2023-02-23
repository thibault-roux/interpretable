import aligned_wer as awer

# We want to visualize word gravity

# how ?
# we know that some corrections implies better gains


from termcolor import colored
class bcolors:
    BLUE    = '\033[94m'
    RED     = '\033[91m'
    YELLOW  = '\033[93m'
    ENDC    = '\033[0m'

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
    
if __name__ == '__main__':
    # ref = input("Reference: ")
    # hyp = input("Hypothesis: ")
    ref = "salut ça va mon beau"
    hyp = "salut va toi mon beau"

    # find word with error. Insert a token for deletion?

    errors, distance = awer.wer(ref.split(" "), hyp.split(" "))
    # print distance et errors pour voir ce que ça fait

    print(errors)
    print(distance)

    print(ref)
    print(hyp)
    newref = add_eps_ref(ref, errors)
    newhyp = add_eps_hyp(hyp, errors)
    print("->")
    print(newref)
    print(newhyp)

    base_errors = ''.join(errors)
    level = {''.join(str(x) for x in [0]*distance)}
    for node in level:
        corrected_hyp = correcter(ref, hyp, node, base_errors)
        score = metric(ref, corrected_hyp, memory)
        # save score and compare