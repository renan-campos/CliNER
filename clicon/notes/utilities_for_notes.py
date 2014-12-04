######################################################################
#  CliNER - utilities.py                                             #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Helper tools for Note objects                            #
######################################################################


import nltk.data
import re


def classification_cmp(a,b):
    """
    concept_cmp()

    Purpose: Compare concept classification tokens
    """
    a = (int(a[1]), int(a[2]))
    b = (int(b[1]), int(b[2]))

    # Sort by line number
    if a[0] < b[0]:
        return -1
    if a[0] > b[0]:
        return  1
    else:
        # Resolve lineno ties with indices
        if a[1] < b[1]:
            return -1
        if a[1] > b[1]:
            return  1
        else:
            return 0



def concept_cmp(a,b):
    """
    concept_cmp()

    Purpose: Compare concept classification tokens
    """
    return a[1][0] < b[1][0]



# Helper function
def lineno_and_tokspan(line_inds, data, text, char_span):
    """ File character offsets => line number and index into line """
    for i,span in enumerate(line_inds):
        if char_span[1] <= span[1]:

            #print
            #print "line-span: ", span

            # start and end of span relative to sentence
            start = char_span[0] - span[0]
            end   = char_span[1] - span[0]

            p = 7558 == char_span[0]#'bowel movement' in text[span[0]:span[1]][start:end]
            if p: print
            if p: print char_span
            if p: print "START: ", start
            if p: print "END: ", end

            #print "USING span on text: ~" + text[span[0]:span[1]] + '~'
            if p: print "USING start and end: ~" + text[span[0]:span[1]][start:end]+'~'

            #print "DATA: ", data[i]
            tok_span = [0,len(data[i])-1]
            char_count = 0

            dataWithEmptyChars = wtokenizer.tokenize(text[span[0]:span[1] + 1])
            #dataWithEmptyChars = data[i]

            index = 0
            beginning_found = False
            for j,tok in enumerate(dataWithEmptyChars):
                if char_count > end:
                    tok_span[1] = index -1
                    break
                elif (beginning_found == False) and (char_count >= start):
                    tok_span[0] = index
                    beginning_found = True
                char_count += len(tok) #+ 1

                val = span[0]+char_count
                if p: print '|' + text[val-3:val+4] + '|' , '(%d)' % char_count
                if p: print '|' + text[val] + '|'

                if len(tok) > 0:
                   index += 1
                if p: print '\t',j, '\t', tok, '(', char_count, ')'

                # Skip ahead to next non-whitespace (doesnt account for EOF)
                #print text
                while text[span[0]+char_count].isspace(): 
                    char_count += 1
                    if (span[0] + char_count) >= len(text):
                        break

            if p: print 'start/end:   ', start, end
            if p: print 'tok_span:    ', tok_span
            if p: print 'text:        ', text[span[0]:span[1]]
            if p: print

            # return line number AND token span
            if p: print "LINE: ", i
            if p: print "TOK SPAN: ", tok_span
            if p: print data[i]

            if p: print "USING char_span on text: ", text[char_span[0]:char_span[1]]
            if p: print "USING tok_span on data[i]", data[i][tok_span[0]], data[i][tok_span[1]]

            return (i, tuple(tok_span))

    return None




# Helper function
def lno_and_tokspan__to__char_span(line_inds, data, text, lineno, tokspan,fname='foo'):
    """ File character offsets => line number and index into line """

    start,end = line_inds[lineno]
    startTok,endTok = tokspan

    dataWithEmpty= wtokenizer.tokenize(text[start:end])

    #print '\n\n\n'
    #print 'start: ', start
    #print 'end:   ', end
    #print 'd: ', text[start:end].replace('\n',' ').replace('\t',' ')
    #print 'dataWith: ', dataWithEmpty
    #print
    #print 'data:     ', data[lineno]
    #print

    # |330||338

    region = text[start:end]
    #print data[lineno][startTok]
    #print text[start:end]
    #print start

    #print

    ind = 0
    for i in range(startTok):
        #print region[ind-4:ind] + '<' + region[ind] + '>' + region[ind+1:ind+5]
        #print ind
        ind += len(dataWithEmpty[i])
        while text[start+ind].isspace(): ind += 1
        #print ind
        #print

    #print
    #print '!!!'
    #print

    '''
    jnd = ind
    for i in range(startTok,endTok+1):
        print region[jnd-4:jnd] + '<' + region[jnd] + '>' + region[jnd+1:jnd+5]
        print jnd
        jnd += len(dataWithEmpty[i])
        while text[start+jnd].isspace(): jnd += 1
        print jnd
        print

    #while text[start+jnd-1].isspace(): jnd -= 1
    '''

    startOfTokRelToText = start + ind
    #endOfTokRelToText   = start + jnd
    endOfTokRelToText   = start + ind + len(dataWithEmpty[startTok])

    #print '---' + text[endOfTokRelToText-3:endOfTokRelToText+4] + '---'

    #print startOfTokRelToText, '  ', endOfTokRelToText
    #if startTok != endTok: exit()

    return startOfTokRelToText,endOfTokRelToText




def span_relationship(s1, s2):
    if (s1[0] <= s2[0]) and (s1[1] >= s2[1]):
        return 'subsumes'
    else: 
        return None



def span_stuff(classifs):

    # Sort all concept spans
    classifs = sorted(classifs, key=lambda s:s[0])

    # Loop until convergence

    newClassifs = []

    for i in range(len(classifs)-1):

        rel = span_relationship(classifs[i], classifs[i+1])

        if rel == 'subsumes':
            #print i, '  -->  ', classifs[i], classifs[i+1]
            s1 = classifs[i]
            s2 = classifs[i+1]

            # Split s1 into leading atom (and leave s2 as second atom)
            #print s1
            #print s2
            #print
            newSpan = (s1[0], s2[0]-1)
            newClassifs.append(newSpan)
        
        else:
            newClassifs.append(classifs[i])

    #print newClassifs
    return newClassifs



# Break file into sentences.
class SentenceTokenizer:

    def __init__(self):
        self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    def tokenize(self, text_file):
        """ Split the document into sentences """
        text = open(text_file, 'r').read()

        # First pass: tokenizer
        first_pass = self.sent_tokenizer.tokenize(text)
        return first_pass

        # Second pass, delimit on '\n'
        #retVal = []
        #for tok in first_pass:
        #    line_split = tok.split('\n')
        #    retVal.append(line_split[0])
        #    for t in line_split[1:]:
        #        #retVal.append('\n')
        #        if t != '': retVal.append(t)
        #return retVal



# Break sentence into words
class WordTokenizer:

    # TODO - PunktWordTokenizer (http://www.nltk.org/api/nltk.tokenize.html)
    def __init__(self):
        pass

    def tokenize(self, sent):
        """ Split the sentence into tokens """
        toks = nltk.tokenize.word_tokenize(sent)

        # Second pass, delimit on token-combiners such as '/' and '-'
        delims = ['/', '-', '(', ')', ',', '.', ':', '*', '[', ']', '%', '+']
        for delim in delims:
            retVal = []
            for tok in toks:
                line_split = tok.split(delim)
                if line_split[0] != '': retVal.append(line_split[0])
                for t in line_split[1:]:
                    retVal.append(delim)
                    if t != '': retVal.append(t)
            toks = retVal

        return retVal




# Instantiate tokenizers
wtokenizer = WordTokenizer()
stokenizer = SentenceTokenizer()
