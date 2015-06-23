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

    >>> a = ('problem', 4, 0, 5)
    >>> b = ('treatment', 2, 0, 3)

    >>> classification_cmp(b,a)
    -1

    >>> classification_cmp(a,a)
    0

    >>> classification_cmp(a,b)
    1
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
    '''
    lineno_and_tokspan()

    Purpose: File character offsets => line number and index into line

    '''

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
            #print "USING char_span on text: ", text[char_span[0]], text[char_span[1]]

            return (i, tuple(tok_span))

    return None




# Helper function
def lno_and_tokspan__to__char_span(line_inds, data, text, lineno, tokspan):
    '''
    lno_and_tokspan__to__char_span()

    Purpose: File character offsets => line number and index into line
    '''

    start,end = line_inds[lineno]

    dataWithEmpty= text[start:end].replace('\n',' ').replace('\t',' ').split(' ')

    print 'start: ', start
    print 'end:   ', end
    print 'dataWith: ', dataWithEmpty
    print
    print 'data:     ', data[lineno]
    print '\n\n\n'

    tokPosRelToSent = []
    count = 0
    for string in dataWithEmptyChars:
        if string != '':
            tokPosRelToSent.append((count, count + len(string)-1))
            count += len(string) + 1
        else:  # empty string
            count += 1

    #print tokPosRelToSent
    #print tokPosRelToSent[startTok:endTok+1]

    startOfTokRelToText = tokPosRelToSent[startTok][0] + start
    endOfTokRelToText   = tokPosRelToSent[  endTok][1] + start

    #print '---' + self.text[endOfTokRelToText-3:endOfTokRelToText+4] + '---'

    #print startOfTokRelToText, '  ', endOfTokRelToText

    # Heuristc / Hack for determining when to include extra space
    if (    self.text[endOfTokRelToText  ].isalpha()) and \
       (not self.text[endOfTokRelToText+1].isalpha()) :
               endOfTokRelToText += 1

    #print startOfTokRelToText, '  ', endOfTokRelToText
    #print '\n'

    if line not in spans:
        spans[line] = (self.fileName + ".text||Disease_Disorder||CUI-less||" + str(startOfTokRelToText) + "||" +  str(endOfTokRelToText))
    else:
        spans[line] += ("\n" + self.fileName + ".text||Disease_Disorder||CUI-less||" + str(startOfTokRelToText) + "||" +  str(endOfTokRelToText))


    print lineno
    print tokspan
    
    line = data[lineno]

    print line

    print

    return 0,0




# Break file into sentences.
class SentenceTokenizer:

    def __init__(self):
        self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    def tokenize(self, text_file):
        """ 
        SentenceTokenize::tokenize()

        Purpose: Split the document into sentences 

        TODO: Add a case for a multi-sentence line

        >>> import os
        >>> base_dir = os.path.join( os.getenv('CLINER_DIR'), 'tests' )
        >>> txt_file = os.path.join(base_dir, 'data', 'multi.txt')

        >>> sent_tokenizer = SentenceTokenizer()
        >>> sent_tokenizer.tokenize(txt_file)
        ['Title :', 'Casey at the Bat', "The outlook wasn't brilliant for the Mudville Nine that day ;", 'The score stood four to two , with but one inning more to play ,']

        """
        # Read data from file
        lines = open(text_file, 'r').read().strip().split('\n')

        # Assume that sentences don't cross newline?
        line_tokens = [ self.sent_tokenizer.tokenize(line) for line in lines ]
        tokens = reduce(lambda a,b: a+b, line_tokens)

        return tokens



# Break sentence into words
class WordTokenizer:

    # TODO - PunktWordTokenizer (http://www.nltk.org/api/nltk.tokenize.html)
    def __init__(self):
        pass

    def tokenize(self, sent):
        """ 
        WordTokenizer::tokenize()

        Purpose: Split the sentence into tokens 
        """
        return sent.split()

