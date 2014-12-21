import sys

def main():

    text_f = '/data1/wboag/clicon/CliCon/clicon/eval/text/08114-027513.text'
    with open(text_f, 'r') as f:
        text = f.read()

    #if 'predict' in sys.argv:
    #    fname = '/data1/wboag/clicon/CliCon/data/test_predictions/00098-016139.pipe'
    if 'gold' in sys.argv:
        fname = '/data1/wboag/clicon/CliCon/clicon/eval/gold/08114-027513.pipe'
    else:
        print '\n\tError: must specify gold OR predict\n'
        exit()

    with open(fname, 'r') as f:
        for line in f.readlines():
            if line == '\n': continue
            parsed = line.strip().split('||')
            stuff = []
            for i in range(3,len(parsed),2):
                start = int(parsed[i  ])
                end   = int(parsed[i+1])
                stuff.append(text[start:end])

            print '%5d %5d' % (start,end), '\t', '|' + '|'.join(stuff) + '|'



if __name__ == '__main__':
    main()
