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

from model import Model
from notes.note import Note


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

    parser.add_argument("-third",
        dest = "third",
        help = "A flag indicating whether to have third/clustering pass",
        action = "store_true"
    )

    args = parser.parse_args()


    # Parse arguments
    files = glob.glob(args.input)
    helper.mkpath(args.output)
    format = args.format
    third = args.third


    # Tell user if not predicting
    if not files:
        print >>sys.stderr, "\n\tNote: You did not supply any input files\n"
        exit()


    # Load model
    model = Model.load(args.model)


    # Predict
    predict(files, model, args.output, format=format, third=third)



def predict(files, model, output_dir, format, third=False):

    # Must specify output format
    if format not in Note.supportedFormats():
        print >>sys.stderr, '\n\tError: Must specify output format'
        print >>sys.stderr,   '\tAvailable formats: ', ' | '.join(Note.supportedFormats())
        print >>sys.stderr, ''
        exit(1)


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
        labels = model.predict(note, third)


        # Output file
        extension = note.getExtension()
        fname = os.path.splitext(os.path.basename(txt))[0] + '.' + extension
        out_path = os.path.join(output_dir, fname)

        # Get predictions in proper format
        note.setFileName(os.path.split(txt)[-1])
        output = note.write(labels)

        #print output

        # Output the concept predictions
        print '\n\nwriting to: ', out_path
        with open(out_path, 'w') as f:
            print >>f, output
        print




if __name__ == '__main__':
    main()
