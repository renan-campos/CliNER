#-------------------------------------------------------------------------------
# Name:        cv.py
#
# Purpose:     Cross validation.
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------



import argparse
import os,sys
import glob
import random


sources = os.path.join(os.getenv('CLICON_DIR'),'clicon')
if sources not in sys.path:
    sys.path.append(sources)

from notes.note import Note
import helper

import train
import predict
import evaluate



def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
        dest = "txt",
        help = "The files that contain the training examples",
        default = os.path.join(os.getenv('CLICON_DIR'),'clicon/eval/text/*.text')
    )

    parser.add_argument("-c",
        dest = "con",
        help = "The files that contain the labels for the training examples",
        default = os.path.join(os.getenv('CLICON_DIR'),'clicon/eval/gold/*.pipe')
    )

    parser.add_argument("-n",
        dest = "length",
        help = "Number of data points to use",
        default = -1
    )

    parser.add_argument("-f",
        dest = "folds",
        help = "Number of folds to partition data into",
        default = 10
    )

    parser.add_argument("-g",
        dest = "grid",
        help = "Perform Grid Search",
        action = "store_true"
    )

    parser.add_argument("-r",
        dest = "random",
        help = "Random shuffling of input data.",
        type = bool,
        default = False
    )


    # Parse the command line arguments
    args = parser.parse_args()


    # Decode arguments
    txt_files = glob.glob(args.txt)
    con_files = glob.glob(args.con)
    length = int(args.length)
    num_folds = int(args.folds)


    # Collect training data file paths
    txt_files_map = helper.map_files(txt_files) #ex.{'record-13':'record-13.con'}
    con_files_map = helper.map_files(con_files)
    training_list = []
    for k in txt_files_map:
        if k in con_files_map:
            training_list.append((txt_files_map[k], con_files_map[k]))


    # display file names (for user to see data was properly located)
    #print '\n', training_list, '\n'


    # For each held-out test set
    i = 1
    for training,testing in cv_partitions(training_list, num_folds=num_folds, shuffle=args.random):

        # Users like to see progress
        print 'Fold: %d of %d' % (i,num_folds)
        i += 1

        print '\t', training

        # Train on non-heldout data
        model_path = os.path.join(os.getenv('CLICON_DIR'),'models','semeval-cv.model')
        model = train.train(training, model_path=model_path, format='semeval', is_crf=True, grid=args.grid, third=True)

        # Predict on held out
        X_test = [ d[0] for d in testing ]
        #X_test = [ d[0] for d in training ]  # Sanity check
        pred_dir= os.path.join(os.getenv('CLICON_DIR'),'clicon','eval','predict')
        predict.predict(X_test, model, pred_dir, format='semeval', third=True)




def cv_partitions( data, num_folds=10, shuffle=True ):

    """
    cross_validation_partitions()

    Purpose: Parition input data for cross validation.

    @param data.    A list of data to partition
                     NOTE: does not look at what each element of the list is
    @param folds.   The number of folds to parition into

    @return         A list (actually generator) of tuples, where:
                       each tuple has (rest, heldout)
    """


    # Shuffle data
    if shuffle:
        random.shuffle(data)


    # Break data into num_folds number of folds
    fold_size = len(data) / num_folds
    folds = []
    for i in range(num_folds):
        f = [ data.pop() for j in range(fold_size) ]
        folds.append(f)


    # Evenly distribute any remaining data
    for i,d in enumerate(data):
        folds[i].append(d)


    # Which fold to hold out?
    for i in range(num_folds):
        heldout = folds[i]
        rest    = [ d   for lst     in folds[:i]+folds[i+1:] for d in lst]

        yield (rest, heldout)



if __name__ == '__main__':
    main()
