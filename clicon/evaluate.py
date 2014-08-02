import os
import os.path
import sys
import argparse
import glob
import helper

from model import Model
from note import *

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
        help = "Test files that were used to generate predictions",
        dest = "txt",
        default = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/test_data/*')
    )

    parser.add_argument("-c",
        help = "The directory that contains predicted concept files organized into subdirectories for svm, lin, srf",
        dest = "con",
        default = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/test_predictions/')
    )

    parser.add_argument("-r",
        help = "The directory that contains reference gold standard concept files",
        dest = "ref",
        default = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/reference_standard_for_test_data/concepts/')
    )

    parser.add_argument("-o",
        help = "Write the evaluation to a file rather than STDOUT",
        dest = "output",
        default = None
    )

    # Parse command line arguments
    args = parser.parse_args()


    # Is output destination specified
    if args.output:
        args.output = open(args.output, "w")
    else:
        args.output = sys.stdout


    txt_files = glob.glob(args.txt)
    ref_files = os.listdir(args.ref)
    ref_files = map(lambda f: os.path.join(args.ref, f), ref_files)

    txt_files_map = helper.map_files(txt_files)
    ref_files_map = helper.map_files(ref_files)

    con_directories = os.listdir(args.con)

    for con_directory in con_directories:
        files = []
        directory_name = os.path.basename(con_directory)

        if directory_name not in ["svm", "crf", "lin"]:
            continue

        con_files = os.listdir(os.path.join(args.con, con_directory))
        con_files = map(lambda f: os.path.join(args.con, con_directory, f), con_files)

        con_files_map = helper.map_files(con_files)

        for k in txt_files_map:
            if k in con_files_map and k in ref_files_map:
                files.append((txt_files_map[k], con_files_map[k], ref_files_map[k]))


        # Compute the confusion matrix
        labels = Model.labels   # hash tabble: label -> index
        confusion = [[0] * len(labels) for e in labels]

        print files
        print ''

        # txt <- medical text
        # con <- model predictions
        # ref <- actual labels
        for txt, con, ref in files:
            
            # A note that represents the model's predictions
            cnote = Note()
            cnote.read_i2b2( txt, con )
            #cnote.read_plain( txt, con )    # in case in plain format

            # A note that is the actual concept labels
            rnote = Note()
            rnote.read_i2b2( txt, ref )
            #rnote.read_plain(txt, ref )    # in case in plain format
            
            predictions = cnote.conlist() 

            #TO DO: make leaner
            #TO DO: create unit tests 
            reference_concept_spans = {} 
            predicted_concept_spans = {} 
           
            for line_index, span in enumerate(rnote.boundaries):
                #obtain each boundary for the reference labels. 
                for boundary_index, boundary in enumerate(span):             
                    #IF none/'O' for references simply add to confusion matrix.
                    #this is done because a blank can only match or mismatch.
                    if boundary == 'O':
                        actual = labels[rnote.conlist()[line_index][boundary_index]]
                        predicted = labels[cnote.conlist()[line_index][boundary_index]]
                        confusion[actual][predicted] += 1
                    #'B' signifies beginning of a concept. 
                    if boundary == 'B': 
                        concept = rnote.concepts[line_index][boundary_index]
                        #create an entry for the line number for this span.  
                        if reference_concept_spans.has_key(line_index) == False:
                            reference_concept_spans[line_index] = {}
                        #mark the beginning of the concept.  
                        beginning = boundary_index 
                        end = boundary_index                          
                        for possible_end in span[boundary_index+1:]:
                            #find the end of the concept 
                            if possible_end == 'B' or possible_end == 'O': 
                                break 
                            if possible_end == 'I':
                                end += 1  
                        #store this concept to its line number. 
                        reference_concept_spans[line_index].update({(beginning,end):concept})
            
            #find the labels generated from predictions.
            #same logic as above except we only care about the labels created for predictions. 
            for line_index, span in enumerate(cnote.boundaries):
                for boundary_index, boundary in enumerate(span):
                    if boundary == 'B':
                        concept = cnote.concepts[line_index][boundary_index]
                        beginning = boundary_index
                        end = boundary_index
                        if predicted_concept_spans.has_key(line_index) == False:
                            predicted_concept_spans[line_index] = {}
                        
                        for possible_end in span[boundary_index+1:]:
                            if possible_end == 'B' or possible_end == 'O':
                                break
                            if possible_end == 'I':
                                end += 1
                        predicted_concept_spans[line_index].update({(beginning,end):concept})
            
            #for each reference span verify if the predicted span corresponds.
            #exatch matches     
            for lines in reference_concept_spans:
                spans_to_remove = []
                for spans in reference_concept_spans[lines]:
                    #if the line does not exist for whatever reason mark it as none. 
                    if (lines in predicted_concept_spans) == False:
                        confusion[labels[reference_concept_spans[lines][spans]]][labels['none']] += 1
                        continue
                    #if the span exists and the concept matches mark it for removal and add to confusion matrix
                    if spans in predicted_concept_spans[lines]: 
                       if reference_concept_spans[lines][spans] == predicted_concept_spans[lines][spans]: 
                          #add to confusion matrix.
                          spans_to_remove.append(spans)    
                          confusion[labels[reference_concept_spans[lines][spans]]][labels[predicted_concept_spans[lines][spans]]] += 1 
                for span_to_remove in spans_to_remove:
                    #prevent double counting. 
                    predicted_concept_spans[lines].pop(span_to_remove)
                    reference_concept_spans[lines].pop(span_to_remove)

            #these left overspans do not have exact matches. 
            #for each reference span see if there is a predict span that it falls in the range of
            #inexact matches
            for lines in reference_concept_spans:
                #if line does not exist for whatever reason just continue, these have already been marked for score. 
                if (lines in predicted_concept_spans) == False:
                    continue
                for ref_spans in reference_concept_spans[lines]:
                    incorrect_classifications = [] 
                    for predicted_spans in predicted_concept_spans[lines]: 
                        #find overlapping spans 
                        if predicted_spans[0] >= ref_spans[0] and predicted_spans[0] <= ref_spans[1] \
                           or predicted_spans[1] >= ref_spans[0] and predicted_spans[1] <= ref_spans[1]:
                            #if the classification matches then mark it for score. 
                            if reference_concept_spans[lines][ref_spans] == predicted_concept_spans[lines][predicted_spans]:
                                confusion[labels[reference_concept_spans[lines][ref_spans]]][labels[predicted_concept_spans[lines][predicted_spans]]] += 1 
                                incorrect_classifications = [] 
                                break 
                            #overlap but incorrect classification. we still store what it gets for now because there may be another overlap
                            #that does match inexactly. 
                            else: 
                                incorrect_classifications.append(predicted_concept_spans[lines][predicted_spans])
                    #if this is greater than 0 then there has been an incorrect classification. just map the first index
                    #it is wrong either way. 
                    if len(incorrect_classifications) > 0:
                        confusion[labels[reference_concept_spans[lines][ref_spans]]][labels[incorrect_classifications[0]]] += 1
                    #if there is no predicted span that overlaps with the reference span just mark as none.  
                    else:
                        confusion[labels[reference_concept_spans[lines][ref_spans]]][labels['none']] += 1
         
        # Display the confusion matrix
        print >>args.output, ""
        print >>args.output, ""
        print >>args.output, ""
        print >>args.output, "================"
        print >>args.output, directory_name.upper() + " RESULTS"
        print >>args.output, "================"
        print >>args.output, ""
        print >>args.output, "Confusion Matrix"
        pad = max(len(l) for l in labels) + 6
        print >>args.output, "%s %s" % (' ' * pad, "\t".join(Model.labels.keys()))
        for act, act_v in labels.items():
            print >>args.output, "%s %s" % (act.rjust(pad), "\t".join([str(confusion[act_v][pre_v]) for pre, pre_v in labels.items()]))
        print >>args.output, ""

        # Compute the analysis stuff
        precision = []
        recall = []
        specificity = []
        f1 = []

        tp = 0
        fp = 0
        fn = 0
        tn = 0

        print >>args.output, "Analysis"
        print >>args.output, " " * pad, "Precision\tRecall\tF1"

        for lab, lab_v in labels.items():
         #   print confusion[lab_v][lab_v]
            tp = confusion[lab_v][lab_v]
            fp = sum(confusion[v][lab_v] for k, v in labels.items() if v != lab_v)
            fn = sum(confusion[lab_v][v] for k, v in labels.items() if v != lab_v)
            tn = sum(confusion[v1][v2] for k1, v1 in labels.items()
              for k2, v2 in labels.items() if v1 != lab_v and v2 != lab_v)
            precision += [float(tp) / (tp + fp + 1e-100)]
            recall += [float(tp) / (tp + fn + 1e-100)]
            specificity += [float(tn) / (tn + fp + 1e-100)]
            f1 += [float(2 * tp) / (2 * tp + fp + fn + 1e-100)]
            print >>args.output, "%s %.4f\t%.4f\t%.4f\t%.4f" % (lab.rjust(pad), precision[-1], recall[-1], specificity[-1], f1[-1])

        print >>args.output, "--------"

        precision = sum(precision) / len(precision)
        recall = sum(recall) / len(recall)
        specificity = sum(specificity) / len(specificity)
        f1 = sum(f1) / len(f1)

        print >>args.output, "Average: %.4f\t%.4f\t%.4f\t%.4f" % (precision, recall, specificity, f1)

if __name__ == '__main__':
    main()

