######################################################################
#  CliNER - replicate.py                                             #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Test writer by outputing hard-coded data                 #
#                                                                    #
#               **Sanity check for reader/writer**                   #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Dec. 18, 2014'


import os
import argparse
import helper

from notes.note import Note




def main():

    # Parse arguments
    txt,con,output_dir,format = parse_the_arguments()


    # Output data to file using writer
    output_filename = write_to_file(txt, format, output_dir)


    # Compare output to gold standard
    compare_answers(output_filename,con)
    



def compare_answers(pred_file, gold_file):

    print 'comparing files'

    print
    print 'pred in: ', pred_file
    print 'gold in: ', gold_file
    print

    print "Oops! This file comparison function han't been implemented"
    print




def write_to_file(txt, format, output_dir):

    # list of classification tuples (the thing that the model would predict)
    #
    # the Note class does not have a method that RETURNS something of this form,
    # but this is the form that its write ACCEPTS
    predictions = [ ('problem', 1 , [(91, 91)         ]) ,
                    ('problem', 1 , [(93, 94)         ]) ,
                    ('problem', 2 , [(16, 16)         ]) ,
                    ('problem', 2 , [(18, 19)         ]) ,
                    ('problem', 2 , [(22, 24)         ]) ,
                    ('problem', 3 , [(16, 18)         ]) ,
                    ('problem', 3 , [(20, 21)         ]) ,
                    ('problem', 4 , [(3 , 3 )         ]) ,
                    ('problem', 5 , [(4 , 5 )         ]) ,
                    ('problem', 6 , [(8 , 9 )         ]) ,
                    ('problem', 9 , [(9 , 11)         ]) ,
                    ('problem', 18, [(0 , 0 ), (4, 5 )]) ,
                    ('problem', 18, [(0 , 0 ), (9, 10)]) ,
                    ('problem', 18, [(6 , 7 )         ]) ,
                    ('problem', 19, [(3 , 4 )         ]) ,
                    ('problem', 19, [(5 , 6 )         ]) ,
                    ('problem', 19, [(8 , 9 )         ]) ,
                    ('problem', 22, [(7 , 8 )         ]) ,
                    ('problem', 23, [(4 , 4 )         ]) ,
                    ('problem', 23, [(11, 11)         ]) ,
                    ('problem', 25, [(2 , 3 )         ]) ,
                    ('problem', 29, [(1 , 3 )         ]) ,
                    ('problem', 29, [(5 , 6 )         ]) ,
                    ('problem', 31, [(24, 25)         ]) ,
                    ('problem', 32, [(12, 12)         ]) ,
                    ('problem', 32, [(16, 17)         ]) ,
                    ('problem', 33, [(16, 17)         ]) ,
                    ('problem', 35, [(11, 12)         ]) ,
                    ('problem', 35, [(13, 16)         ]) ,
                    ('problem', 36, [(4 , 5 )         ]) ]

    # Read the data into a Note object
    note = Note(format)
    note.read(txt)

    # Create output file path
    helper.mkpath(output_dir)
    extension = note.getExtension()
    fname = os.path.splitext(os.path.basename(txt))[0] + '.' + extension
    out_path = os.path.join(output_dir, fname)

    # Get predictions in proper format
    note.setFileName(os.path.split(txt)[-1])
    output = note.write(predictions)

    # Output the concept predictions
    print '\n\nwriting to: ', out_path
    with open(out_path, 'w') as f:
        print >>f, output
    print

    # return name of output file
    return out_path





def parse_the_arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument("-t", 
        dest = "txt", 
        help = "The input files to predict", 
        default = os.path.join(os.getenv('CLICON_DIR'), 'clicon/eval/text/00098-016139.text')
    )

    parser.add_argument("-c",
        dest = "con",
        help = "The files that contain the labels for the training examples",
        default = os.path.join(os.getenv('CLICON_DIR'), 'clicon/eval/gold/00098-016139.pipe')
    )

    parser.add_argument("-o", 
        dest = "output", 
        help = "The directory to write the output", 
        default = os.path.join(os.getenv('CLICON_DIR'), 'data/test_predictions')
    )

    args = parser.parse_args()

    txt = args.txt
    con = args.con
    output_dir = args.output
    format = 'semeval'

    return (txt, con, output_dir, format)




if __name__ == '__main__':
    main()
