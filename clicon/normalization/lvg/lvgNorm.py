import os
from subprocess import Popen, PIPE, STDOUT

def lvgNormalize(string):

    normAppPath = (os.environ["CLICON_DIR"] + "/clicon/normalization/lvg/lvg/bin/norm")

    process = Popen([normAppPath], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout_data = process.communicate(input=string)[0]

    # remove final new line
    stdout_data = stdout_data[:-1]

    # break stdout into a list of strings. one strin for each line.
    stdout_data = stdout_data.split('\n')

    normalizedStrings = []
#    print stdout_data
    # obtain the normalized versions of the string
    for line in stdout_data:
        normalizedStrings.append(line.split('|')[1])

    return normalizedStrings

if __name__ == "__main__":

    print "input string to normalize:"

    string = input()

    print "normalization of string"

    print lvgNormalize(string)
