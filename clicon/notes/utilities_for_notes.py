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
            #print "span: ", span

            # start and end of span relative to sentence
            start = char_span[0] - span[0]
            end   = char_span[1] - span[0]

            #print "START: ", start
            #print "END: ", end

            #print "USING span on text: ~" + text[span[0]:span[1]] + '~'
            #print "USING start and end: ~" + text[span[0]:span[1]][start:end]+'~'

            #print "data", data[i]
            tok_span = [0,len(data[i])-1]
            char_count = 0

            dataWithEmptyChars = re.split(" |\n|\t", text[span[0]:span[1] + 1])

            index = 0
            for j,tok in enumerate(dataWithEmptyChars):
                if char_count > end:
                    tok_span[1] = index -1
                    break
                elif char_count == start:
                    tok_span[0] = index
                char_count += len(tok) + 1
                if len(tok) > 0:
                   index += 1
                #print '\t',j, '\t', tok, '(', char_count, ')'

            #print start, end
            #print tok_span
            #print text[span[0]:span[1]]
            #print data[i][tok_span[0]:tok_span[1]]
            #print

            # return line number AND token span
            #print "LINE: ", i
            #print "TOK SPAN: ", tok_span
            #print data[i]
            #print tok_span

            #print "USING char_span on text: ", text[char_span[0]:char_span[1]]
            #print "USING tok_span on data[i]", data[i][tok_span[0]], data[i][tok_span[1]]

            return (i, tuple(tok_span))

    return None




# Helper function
def lno_and_tokspan__to__char_span(line_inds, data, text, lineno, tokspan,fname='foo'):
    """ File character offsets => line number and index into line """

    start,end = line_inds[lineno]
    startTok,endTok = tokspan

    dataWithEmpty= text[start:end].replace('\n',' ').replace('\t',' ').split(' ')

    #print '\n\n\n'
    #print 'start: ', start
    #print 'end:   ', end
    #print 'd: ', text[start:end].replace('\n',' ').replace('\t',' ')
    #print 'dataWith: ', dataWithEmpty
    #print
    #print 'data:     ', data[lineno]

    tokPosRelToSent = []
    count = 0
    for string in dataWithEmpty:
        if string != '':
            tokPosRelToSent.append((count, count + len(string)-1))
            count += len(string) + 1
        else:  # empty string
            count += 1

    startOfTokRelToText = tokPosRelToSent[startTok][0] + start
    endOfTokRelToText   = tokPosRelToSent[  endTok][1] + start

    #print '---' + text[endOfTokRelToText-3:endOfTokRelToText+4] + '---'

    #print startOfTokRelToText, '  ', endOfTokRelToText

    # Heuristc / Hack for determining when to include extra space
    if (    text[endOfTokRelToText  ].isalpha()) and \
       (not text[endOfTokRelToText+1].isalpha()) :
               endOfTokRelToText += 1

    #print startOfTokRelToText, '  ', endOfTokRelToText
    #print '\n'

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
        return self.sent_tokenizer.tokenize(text)



# Break sentence into words
class WordTokenizer:

    # TODO - PunktWordTokenizer (http://www.nltk.org/api/nltk.tokenize.html)
    def __init__(self):
        pass

    def tokenize(self, sent):
        """ Split the sentence into tokens """
        return sent.split()

