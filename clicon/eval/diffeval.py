#
#  Willie Boag
#
#  Diff of semeval predictions (ignoring CUIs)
#


import sys
import commands
import os
import glob



def main():

    # Get arguments
    if len(sys.argv) != 3:
        print >>sys.stderr, 'usage: %s pred.pipe gold.pipe' % sys.argv[0]
        exit()


    # Get prediction data
    pred = []
    for pred_file in glob.glob(sys.argv[1]):
        with open(pred_file, 'r') as f:
            pred += f.readlines()


    # Get gold data
    gold = []
    for gold_file in glob.glob(sys.argv[2]):
        with open(gold_file, 'r') as f:
            gold = f.readlines()

    # Modify gold file to normlaize CUIs
    tmp_out = 'tmp-file.txt'
    normalized = []
    with open(tmp_out, 'w') as f:
        for line in gold:
            # Set CUI field to 'CUI-less'
            data = line.split('||')
            data[2] = 'CUI-less'
            print >>f, '||'.join(data)
            normalized.append( '||'.join(data) )


    # False positives
    fp = []
    for p in pred:
        if p == '\n': continue
        if p not in normalized:
            print 'FP: ', p.strip('\n')
            fp.append(p)

    print
    
    # False negatives
    fn = []
    for g in normalized:
        if g == '\n': continue
        if g not in pred:
            print 'FN: ', g.strip('\n')
            fp.append(g)
    



if __name__ == '__main__':
    main()
