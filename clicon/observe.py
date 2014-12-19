import sys

def main():

    text_f = '/data1/wboag/clicon/CliCon/clicon/eval/text/00098-016139.text'
    with open(text_f, 'r') as f:
        text = f.read()

    if 'predict' in sys.argv:
        fname = '/data1/wboag/clicon/CliCon/data/test_predictions/00098-016139.pipe'
    elif 'gold' in sys.argv:
        fname = '/data1/wboag/clicon/CliCon/clicon/eval/gold/00098-016139.pipe'
    else:
        print '\n\tError: must specify gold OR predict\n'
        exit()

    with open(fname, 'r') as f:
        for line in f.readlines():
            if line == '\n': continue
            parsed = line.strip().split('||')
            start = int(parsed[3])
            end   = int(parsed[4])
            print '%5d %5d' % (start,end), '\t', '|' + text[start:end] + '|'



if __name__ == '__main__':
    main()
