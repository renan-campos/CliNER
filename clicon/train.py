######################################################################
#  CliNER - train.py                                                 #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Build model for given training data.                     #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Oct. 5, 2014'


import os
import os.path
import glob
import argparse
import cPickle as pickle

import helper
from sets import Set
from model import Model
from notes.note import Note


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", 
        dest = "txt", 
        help = "The files that contain the training examples",
        default = os.path.join(os.getenv('CLICON_DIR'), 'data/train/txt/*')
    )
    
    parser.add_argument("-c", 
        dest = "con", 
        help = "The files that contain the labels for the training examples",
        default = os.path.join(os.getenv('CLICON_DIR'), 'data/train/con/*')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "Path to the model that should be generated",
        default = os.path.join(os.getenv('CLICON_DIR'), 'models/run.model')
    )

    parser.add_argument("-f",
        dest = "format",
        help = "Data format ( " + ' | '.join(Note.supportedFormats()) + " )",
        default = 'i2b2'
    )

    parser.add_argument("-g",
        dest = "grid",
        help = "A flag indicating whether to perform a grid search",
        action = "store_true"
    )

    parser.add_argument("-no-crf",
        dest = "nocrf",
        help = "A flag indicating whether to use crfsuite for pass one.",
        action = "store_true"
    )

    parser.add_argument("-third",
        dest = "third",
        help = "A flag indicating whether to have third/clustering pass",
        action = "store_true"
    )

    # Parse the command line arguments
    args = parser.parse_args()
    is_crf = not args.nocrf
    third = args.third


    # A list of text    file paths
    # A list of concept file paths
    txt_files = glob.glob(args.txt)
    con_files = glob.glob(args.con)


    # data format
    format = args.format


    # Must specify output format
    if format not in Note.supportedFormats():
        print >>sys.stderr, '\n\tError: Must specify output format'
        print >>sys.stderr,   '\tAvailable formats: ', ' | '.join(Note.supportedFormats())
        print >>sys.stderr, ''
        exit(1)


    # Collect training data file paths
    txt_files_map = helper.map_files(txt_files) # ex. {'record-13': 'record-13.con'}
    con_files_map = helper.map_files(con_files)
    
    training_list = []                          # ex. training_list =  [ ('record-13.txt', 'record-13.con') ]
    for k in txt_files_map:
        if k in con_files_map:
            training_list.append((txt_files_map[k], con_files_map[k]))


    # display file names (for user to see data was properly located)
    print '\n', training_list, '\n'


    # Train the model
    train(training_list, args.model, format, is_crf=is_crf, grid=args.grid, third=third)



def train(training_list, model_path, format, is_crf=True, grid=False, third=False):

    """
    train()

    Purpose: Train a model for given clinical data.

    @param training_list  list of (txt,con) file path tuples (training instances)
    @param model_path     string filename of where to pickle model object
    @param format         concept file data format (ex. i2b2, semeval)
    @param is_crf         whether first pass should use CRF classifier
    @param grid           whether second pass should perform grid search
    @param third          whether to perform third/clustering pass
    """

    # Read the data into a Note object
    notes = []
    for txt, con in training_list:
        note_tmp = Note(format)       # Create Note
        note_tmp.read(txt, con)       # Read data into Note
        notes.append(note_tmp)        # Add the Note to the list


    # file names
    if not notes:
        print 'Error: Cannot train on 0 files. Terminating train.'
        return 1


    # Create a Machine Learning model
    model = Model(is_crf=is_crf)


    # Train the model using the Note's data
    model.train(notes, grid, third)


    # Pickle dump
    print 'pickle dump'
    with open(model_path, "wb") as m_file:
        pickle.dump(model, m_file)


    # return trained model
    return model



if __name__ == '__main__':
    main()
