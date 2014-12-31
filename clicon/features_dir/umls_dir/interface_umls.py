#
# Interface to UMLS Databases and concept trie
#
#
#


import copy 
import sqlite3
import create_sqliteDB
import os 

import create_trie
import difflib
import string
import sys

sys.path.append((os.environ["CLICON_DIR"] + "/clicon/normalization/spellCheck"))

from spellChecker import spellCheck

############################################
###          Setups / Handshakes         ###
############################################


#connect to UMLS database 
def SQLConnect():
    #try to connect to the sqlite database.
    db_path = os.path.join( os.environ['CLICON_DIR'], "umls_tables/umls.db")
    if( os.path.isfile( db_path ) ):
        print "\ndb exists" 
    else:
        # Database does not exit. Make one.
        print "\ndb doesn't exist"
        create_sqliteDB.create_db() 

    db = sqlite3.connect( db_path )
    return db.cursor()




############################################
###      Global reource connections      ###
############################################


# Global database connection
c = SQLConnect()

# Global trie
trie = create_trie.create_trie()




############################################
###           Query Operations           ###
############################################


def string_lookup( string ):
    """ Get sty for a given string """
    try:
        c.execute( "SELECT sty FROM MRCON a, MRSTY b WHERE a.cui = b.cui AND str = ?; " , (string,) )
        return c.fetchall()
    except sqlite3.ProgrammingError, e:
        return []


def cui_lookup( string ):
    """ get cui for a given string """
    try:
        # Get cuis
        c.execute( "SELECT cui FROM MRCON WHERE str = ?;" , (string,) )
        return c.fetchall() 
    except sqlite3.ProgrammingError, e:
        return []

def abr_lookup( string ):
    """ searches for an abbreviation and returns possible expansions for that abbreviation"""
    try:
        c.execute( "SELECT str FROM LRABR WHERE abr = ?;", (string,))
        return c.fetchall()
    except sqlite3.ProgrammingError, e:
        return []

def tui_lookup( string ):
    """ takes in a concept id string (ex: C00342143) and returns the TUI of that string which represents the semantic type is belongs to """
    try:
        c.execute( "SELECT tui FROM MRSTY WHERE cui = ?;", (string,))
        return c.fetchall()
    except sqlite3.ProgrammingError, e:
        return []

def substrs_that_exists( lOfStrs , pwl):
    """ sees if a sub string exists within trie"""

    lOfNormStrs = [string.strip() for string in lOfStrs]
    lOfNormStrs = [strip_punct(string) for string in lOfNormStrs]
    lOfNormStrs = [( string, string.lower() ) for string in lOfNormStrs]

    retVal = False

    numThatExist = 0

    # strings are case sensitive.
    for normStr1, normStr2 in lOfNormStrs:

        strs = difflib.get_close_matches(normStr1, trie.keys( unicode( normStr1 ) ), cutoff=.8)
        if len(strs) == 0:
            if normStr2 != normStr1:
                strs = difflib.get_close_matches(normStr2, trie.keys( unicode( normStr2 ) ), cutoff=.8)
            if len(strs) == 0:

                spellChecked = spellCheck(normStr1, PyPwl=pwl)
                strs = difflib.get_close_matches(spellChecked, trie.keys( unicode( spellChecked ) ), cutoff=.8)

            if len(strs) == 0:                               
                spellChecked = spellCheck(normStr2, PyPwl=pwl)
                strs = difflib.get_close_matches(spellChecked, trie.keys( unicode( spellChecked ) ), cutoff=.8)


        if len(strs) > 0:
            numThatExist += 1

    return numThatExist

def strip_punct(stringArg):

    for c in string.punctuation:
        stringArg = string.replace(stringArg, c, "")

    return stringArg

def concept_exists( string ):
    """ Fast query for set membership in trie """
    return string in trie
