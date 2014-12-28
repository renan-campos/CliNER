import cPickle as pickle
import enchant
import os
import sys
import difflib

umls_spell_check_dir = os.environ["CLICON_DIR"] + "/clicon/normalization/spellCheck"

umls_words_file_path = umls_spell_check_dir + "/umls_words.txt"

def getPWL():

#    print umls_words_file_path

    print "loading personal word list"
    pwl = enchant.DictWithPWL(None, umls_words_file_path)
    print "finished loading pwl"

    return pwl

def spellCheck(string, strLen=0, PyPwl=None):
    """
    takes a string, breaks on white space
    and then corrects each string of character count greater than strLen

    strLen is how long the string needs to be before it is checked for spelling.

    PyPwl is a pyenchant personal word list object.
    """

    if PyPwl is None:
        print "NOT using personal word list"
        spellChecker = enchant.Dict("en_US")

    else:
        print "using personal word list"
        spellChecker = PyPwl

    tokenizedString = string.split(' ')

    spellCheckedTokens = []

    for token in tokenizedString:

        # token may be spelled wrong.
        if len(token) > strLen and spellChecker.check(token) is False and spellChecker.check(token.lower()) is False:

             try:
                 suggestions = spellChecker.suggest(token)
                 suggestions = difflib.get_close_matches(token, suggestions, cutoff=.8)

             except:
                 suggestions = []

             if len(suggestions) > 0:
                  # correct potential misspelling
                  spellCheckedTokens.append( suggestions[0] )
             else:
                  # token may be spelled wrong but cannot get a correction to spelling
                  spellCheckedTokens.append(token)

        else:

            spellCheckedTokens.append( token )

    return ' '.join(spellCheckedTokens)

if __name__ == "__main__":

    pwl = getPWL()

    print "input string to spell check"

    string = input ()

    print spellCheck( string, PyPwl=pwl )
