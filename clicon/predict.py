######################################################################
#  CliNER - predict.py                                               #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Use trained model to predict concept labels for data.    #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Oct. 5, 2014'


import os
import sys
import glob
import argparse
import helper
import re

from model import Model
from notes.note import Note

from features_dir.cuiLookup.cuiLookup import getConceptId

import itertools
import cPickle as pickle

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-i", 
        dest = "input", 
        help = "The input files to predict", 
        default = os.path.join(os.getenv('CLICON_DIR'), 'data/test_data/*')
    )

    parser.add_argument("-o", 
        dest = "output", 
        help = "The directory to write the output", 
        default = os.path.join(os.getenv('CLICON_DIR'), 'data/test_predictions')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The model to use for prediction",
        default = os.path.join(os.getenv('CLICON_DIR'), 'models/run.model')
    )

    parser.add_argument("-f",
        dest = "format",
        help = "Data format ( " + ' | '.join(Note.supportedFormats()) + " )", 
        default = 'i2b2'
    )

    parser.add_argument("-crf",
        dest = "with_crf",
        help = "Specify where to find crfsuite",
 
      default = None
    )

    args = parser.parse_args()


    # Parse arguments
    files = glob.glob(args.input)
    helper.mkpath(args.output)
    format = args.format


    # Predict
    predict(files, args.model, args.output, format=format)



def predict(files, model_path, output_dir, format):

    # Must specify output format
    if format not in Note.supportedFormats():
        print >>sys.stderr, '\n\tError: Must specify output format'
        print >>sys.stderr,   '\tAvailable formats: ', ' | '.join(Note.supportedFormats())
        print >>sys.stderr, ''
        exit(1)



    # Load model
    model = Model.load(model_path)


    # Tell user if not predicting
    if not files:
        print >>sys.stderr, "\n\tNote: You did not supply any input files\n"
        exit()


    # For each file, predict concept labels
    n = len(files)
    for i,txt in enumerate(sorted(files)):

        # Read the data into a Note object
        note = Note(format)
        note.read(txt)


        print '-' * 30
        print '\n\t%d of %d' % (i+1,n)
        print '\t', txt, '\n'


        # Predict concept labels
        labels = model.predict(note)

        # Output file
        extension = note.getExtension()
        fname = os.path.splitext(os.path.basename(txt))[0] + '.' + extension
        out_path = os.path.join(output_dir, fname)

        # Get predictions in proper format
        note.setFileName(os.path.split(txt)[-1])
        output = note.write(labels)

        # task B
        if format == "semeval":
            # for the spans generated obtain concept ids of phrase
            output = taskB(output, txt)

        # Output the concept predictions
        print '\n\nwriting to: ', out_path
        with open(out_path, 'w') as f:
            print >>f, output
        print

def taskB(outputArg, txtFile):
    """
    obtains concept ids for each phrase indicated by the span generated from prediction
    """

    txtFile = open(txtFile, "r")

    txtFile = txtFile.read()

    # remove end new line since it is junk.
    output = outputArg[:-1]

    # turn output into a list of strings.
    output = output.split('\n')

    cuisToInsert = []

    for index, line in enumerate(output):

        line = line.split("||")

        phrase = ""

        # get the phrase  for each span
        for span in pairwise(line[3:]):

            string = txtFile[int(span[0]):int(span[1])+1]

            phrase += string

        # concept Id of phrase
        conceptId = obtainConceptId(phrase)

        cuiToInsert = {}

        cuiToInsert["index"] = index
        cuiToInsert["cui"] = conceptId
 
        cuisToInsert.append(cuiToInsert)

    for cuiToInsert in cuisToInsert:
        # replace CUI-less with concept id obtained
        string = output[cuiToInsert["index"]]

        string = re.sub("CUI-less", cuiToInsert["cui"], string)

        output[cuiToInsert["index"]] = string

    # gets end new line back when hoining
    output += [""]

    resultingOutput = "\n".join(output)

    return resultingOutput

def obtainConceptId(phrase):
    """
    calls the function obtainConceptId from the python module cuiLookup
    and obtains concept id of the most frequent concept id.
    """

    # sets are not indexable so convert for indexing.
    # getConceptId returns dictionary of the form {"text":"text argument", "concept_ids":Set([..])}
    conceptIds = getConceptId(phrase)["concept_ids"]

    if conceptIds is None:
        conceptId = "CUI-less"
    else:

        # TODO: add more ways of determining correct concept id when given more then one by metamap.
        conceptId = getMostFrequentCui(list(conceptIds))

    return conceptId

def getMostFrequentCui(cuiList):
    cui_freq = pickle.load(open(os.getenv('CLICON_DIR')+"/cui_freq/cui_freq","rb"))

    cuiWithHighestFreq = None

    for cui in cuiList:

        if cui in cui_freq:

            # sets an initial cui
            if cuiWithHighestFreq is None:
                cuiWithHighestFreq = cui

            # assign new highest
            elif cui_freq[cui] > cui_freq[cuiWithHighestFreq]:
                cuiWithHighestFreq = cui 

    # at this point we have not found any concept ids with a frequency greater than 0.
    # good chance it is CUI-less
    if cuiWithHighestFreq is None:
        cuiWithHighestFreq = "CUI-less"

    return cuiWithHighestFreq

if __name__ == '__main__':
    main()
