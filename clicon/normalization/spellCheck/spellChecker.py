import enchant


def spellCheck(string, strLen=3):
    """
    takes a string, breaks on white space
    and then corrects each string of character count greater
    than 3 for spelling.

    strLen is how long the string needs to be before it is checked for spelling.

    TODO: maybe incorporate umls strings from database somewhere.
    """

    spellChecker = enchant.Dict("en_US")

    tokenizedString = string.split(' ')

    spellCheckedTokens = []

    for token in tokenizedString:

        # token may be spelled wrong.
        if len(token) > strLen and spellChecker.check(token) is False:

             suggestions = spellChecker.suggest(token)        

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

    print "input string to spell check"

    string = input ()

    print spellCheck( string )
