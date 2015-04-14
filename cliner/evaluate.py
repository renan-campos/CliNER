######################################################################
#  CliNER - evaluate.py                                              #
#                                                                    #
#  Kevin Wacome                                   kwacome@cs.uml.edu #
#                                                                    #
#  Purpose: Evaluate predictions of concept labels against gold.     #
######################################################################


__author__ = 'Kevin Wacome'
__date__   = 'Aug. 20, 2014'



import os
import sys
import argparse
import glob
import helper
from copy import deepcopy

from notes.note import Note
from notes.note import concept_labels as labels

def containsSpan(s1, s2):
    return (s1[0] <= s2[0]) and (s2[1] <= s1[1])

def spanOverlap(s1, s2):
    if s2[0] <= s1[0] <= s2[1]: return True
    if s2[0] <= s1[1] <= s2[1]: return True
    if s1[0] <= s2[0] <= s1[1]: return True
    if s1[0] <= s2[1] <= s1[1]: return True
    return False

def getConceptSpans(boundaries, classifications):

    conceptSpans = {}

    for lineIndex, span in enumerate(boundaries):
        for boundaryIndex, boundary in enumerate(span):
            if boundary == 'B':

                concept = classifications[lineIndex][boundaryIndex]
                beginning = boundaryIndex
                end = boundaryIndex

                if conceptSpans.has_key(lineIndex) == False:
                    conceptSpans[lineIndex] = {}

                for possibleEnd in span[boundaryIndex+1:]:
                    if possibleEnd == 'B' or possibleEnd == 'O':
                        break
                    if possibleEnd == 'I':
                        end += 1
                conceptSpans[lineIndex].update({(beginning,end):concept})

    return conceptSpans

def evaluate(referenceSpans, predictedSpans, exactMatch=False, reportSeperately=False):

    #used to generate a dictionary of dictionaries
    #of the form measuresForClasses["treatment"]["True Positives"] -> Number of True Positives for treatment classes
    classes = [
                "treatment",
                "problem",
                "test"
              ]

    measures = {
                "True Positives":0,
                "False Negatives":0,
                "False Positives":0
               }

    confusion = [[0] * len(labels) for e in labels]

    #TO DO: figure out how to report concepts seperately and have it work with reporting together as well.

    measuresForClasses = {classKey:deepcopy(measures) for classKey in dict.fromkeys(classes)}

    falseNegs = []

    for line in referenceSpans:

            #if the line does not exist for whatever reason for all spans on that line
            #mark them as false negative
            if line not in predictedSpans:
                for spanNotInPredictedSpan in referenceSpans[line]:
                    classification = referenceSpans[line][spanNotInPredictedSpan]
                    measuresForClasses[classification]["False Negatives"] +=1
                    confusion[labels[classification]][labels['none']] += 1
                continue

            if exactMatch == True:

                for span in referenceSpans[line]:

                    classInRefSpan = referenceSpans[line][span]

                    # if the span exists & concept matches, then true positive
                    if span in predictedSpans[line]:

                        classInPredSpan = predictedSpans[line][span]

                        if referenceSpans[line][span] == predictedSpans[line][span]:
                            measuresForClasses[classInRefSpan]["True Positives"] += 1
                        else:
                            measuresForClasses[classInRefSpan]["False Negatives"] += 1
                        confusion[labels[classInRefSpan]][labels[classInPredSpan]] += 1
                        predictedSpans[line].pop(span)

                    else:

                        overlap = False
                        for pSpan,v in  predictedSpans[line].items():
                            #if containsSpan(span, pSpan):
                            if spanOverlap(span, pSpan): # or spanOverlap(pSpan,span):
                                overlap = True

                        if not overlap:
                            measuresForClasses[classInRefSpan]["False Negatives"] += 1
                            confusion[labels[classInRefSpan]][labels['none']] += 1

            else:

                #find true positives for inexact spans
                accountedFor = {}
                for span in referenceSpans[line]:

                    accountedFor[span] = False
                    classInRefSpan = referenceSpans[line][span]

                    longestMatchingSpanWithMatchingClassification = {"Predicted Span":None, "Predicted Span length":None, "Predicted Concept":None}


                    for predictedSpan in predictedSpans[line]:

                        classinPredSpan = predictedSpans[line][predictedSpan]

                        #FIND LONGEST OVERLAP
                        if predictedSpan[0] >= span[0] and predictedSpan[0] <= span[1] \
                           or predictedSpan[1] >= span[0] and predictedSpan[1] <= span[1]:

                         #find longest span with match
                            if classInRefSpan == classinPredSpan:

                                if longestMatchingSpanWithMatchingClassification["Predicted Span length"] <(predictedSpan[1] - predictedSpan[0]):
                                    longestMatchingSpanWithMatchingClassification["Predicted Span length"] = (predictedSpan[1] - predictedSpan[0])
                                    longestMatchingSpanWithMatchingClassification["Predicted Concept"] = classinPredSpan
                                    longestMatchingSpanWithMatchingClassification["Predicted Span"] = predictedSpan

                    #if there is an overlapping concept match report true positive
                    if longestMatchingSpanWithMatchingClassification['Predicted Span'] != None:
                        accountedFor[span] = True
                        measuresForClasses[classInRefSpan]["True Positives"] += 1
                        confusion[labels[classInRefSpan]][labels[longestMatchingSpanWithMatchingClassification["Predicted Concept"]]] += 1
                        predictedSpans[line].pop(longestMatchingSpanWithMatchingClassification["Predicted Span"])


                #find the false negatives for inexact spans
                for span in referenceSpans[line]:
                    #already accounted for
                    if accountedFor[span] == True:
                        continue

                    classInRefSpan = referenceSpans[line][span]

                    longestMatchingSpan = {"Predicted Span":None, "Predicted Span length":None, "Predicted Concept":None}
                    for predictedSpan in predictedSpans[line]:
                        classinPredSpan = predictedSpans[line][predictedSpan]

                        #FIND LONGEST OVERLAP
                        if predictedSpan[0] >= span[0] and predictedSpan[0] <= span[1] \
                           or predictedSpan[1] >= span[0] and predictedSpan[1] <= span[1]:

                            if longestMatchingSpan["Predicted Span length"] <(predictedSpan[1] - predictedSpan[0]):
                                longestMatchingSpan["Predicted Span length"] = (predictedSpan[1] - predictedSpan[0])
                                longestMatchingSpan["Predicted Concept"] = classinPredSpan
                                longestMatchingSpan["Predicted Span"] = predictedSpan

                    if longestMatchingSpan['Predicted Span'] != None:
                        measuresForClasses[classInRefSpan]["False Negatives"] += 1
                        confusion[labels[classInRefSpan]][labels[longestMatchingSpan["Predicted Concept"]]] += 1
                        predictedSpans[line].pop(longestMatchingSpan["Predicted Span"])
                    else:
                        measuresForClasses[classInRefSpan]["False Negatives"] += 1
                        confusion[labels[classInRefSpan]][labels['none']] += 1
                        #predictedSpans[line].pop(span)


    #for all the spans that are in predicted that are left. these are false positives
    #as they do not occur in the reference spans.
    leftover = deepcopy(predictedSpans)
    for line in predictedSpans:
        for span in predictedSpans[line]:

            classInPredSpan = predictedSpans[line][span]

            if True:
                measuresForClasses[classInPredSpan]["False Positives"] += 1
                confusion[labels['none']][labels[classInPredSpan]] += 1
                leftover[line].pop(span)


    #if false then do not report concepts
    if reportSeperately == False:
        truePositive = 0
        falseNegative = 0
        falsePositive = 0
        for dictKey in measuresForClasses:
            truePositive += measuresForClasses[dictKey]["True Positives"]
            falseNegative += measuresForClasses[dictKey]["False Negatives"]
            falsePositive += measuresForClasses[dictKey]["False Positives"]

        return {"True Positives":truePositive, "False Negatives":falseNegative, "False Positives":falsePositive}
    else:
        return confusion

def displayMatrix(out, name, confusion):
    # Display the confusion matrix
    print >>out, ""
    print >>out, ""
    print >>out, ""
    print >>out, "================"
    print >>out, name + " RESULTS"
    print >>out, "================"
    print >>out, ""
    print >>out, "Confusion Matrix"
    pad = max(len(l) for l in labels) + 6
    print >>out, "%s %s" % (' ' * pad, "\t".join(labels.keys()))
    for act, act_v in labels.items():
        print >>out, "%s %s" % (act.rjust(pad), "\t".join([str(confusion[act_v][pre_v]) for pre, pre_v in labels.items()]))
    print >>out, ""


    # Compute the analysis stuff
    precision = []
    recall = []
    specificity = []
    f1 = []

    tp = 0
    fp = 0
    fn = 0
    tn = 0

    print >>out, "Analysis"
    print >>out, " " * pad, "Precision\tRecall\tF1"


    for lab, lab_v in labels.items():
        if lab == 'none': continue

        tp = confusion[lab_v][lab_v]
        fp = sum(confusion[v][lab_v] for k, v in labels.items() if v != lab_v)
        fn = sum(confusion[lab_v][v] for k, v in labels.items() if v != lab_v)

        precision += [float(tp) / (tp + fp + 1e-100)]
        recall += [float(tp) / (tp + fn + 1e-100)]
        f1 += [float(2 * tp) / (2 * tp + fp + fn + 1e-100)]
        print >>out, "%s %.4f\t%.4f\t%.4f" % (lab.rjust(pad), precision[-1], recall[-1], f1[-1])

    print >>out, "--------"

    precision = sum(precision) / len(precision)
    recall = sum(recall) / len(recall)
    f1 = sum(f1) / len(f1)

    print >>out, "Average: %.4f\t%.4f\t%.4f" % (precision, recall, f1)



def generateResultsForExactSpans(truePositive, falseNegative, falsePositive):

    #convert to float implicitly incase of any truncation
    truePositive = float(truePositive)
    flaseNegative = float(falseNegative)
    falsePositive = float(falsePositive)

    recall = truePositive / (truePositive + falseNegative)
    precision = truePositive / (truePositive + falsePositive)
    fScore = (2*truePositive) / (2*truePositive + falseNegative + falsePositive)

    #convert to percent
    return {"Recall":(recall * 100), "Precision":(precision * 100), "F Score":(fScore * 100)}




def main():

    parser = argparse.ArgumentParser()

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    parser.add_argument("-t",
        help = "Text files that were used to generate predictions",
        dest = "txt",
        default = os.path.join(BASE_DIR, 'data/test_data/*')
    )

    parser.add_argument("-c",
        help = "The directory that contains predicted concept files organized into subdirectories for svm, lin, srf",
        dest = "con",
        default = os.path.join(BASE_DIR, 'data/test_predictions/')
    )

    parser.add_argument("-r",
        help = "The directory that contains reference gold standard concept files",
        dest = "ref",
        default = os.path.join(BASE_DIR, 'data/reference_standard_for_test_data/concepts/')
    )

    parser.add_argument("-f",
        dest = "format",
        help = "Data format ( " + ' | '.join(Note.supportedFormats()) + " )",
        default = 'i2b2'
    )

    parser.add_argument("-o",
        help = "Write the evaluation to a file rather than STDOUT",
        dest = "output",
        default = None
    )

    # Parse command line arguments
    args = parser.parse_args()
    format = args.format


    # Is output destination specified?
    if args.output:
        args.output = open(args.output, "w")
    else:
        args.output = sys.stdout


    # Must specify output format
    if format not in Note.supportedFormats():
        print >>sys.stderr, '\n\tError: Must specify output format'
        print >>sys.stderr,   '\tAvailable formats: ', ' | '.join(Note.supportedFormats())
        print >>sys.stderr, ''
        exit(1)


    # List of medical text
    txt_files = glob.glob(args.txt)
    txt_files_map = helper.map_files(txt_files)
    wildcard = '*.' + Note.dictOfFormatToExtensions()[format]


    # List of gold data
    ref_files = glob.glob( os.path.join(args.ref, wildcard) )
    ref_files_map = helper.map_files(ref_files)


    # List of predictions
    pred_files = glob.glob( os.path.join(args.con, wildcard) )
    pred_files_map = helper.map_files(pred_files)


    # Grouping of text, predictions, gold
    files = []
    for k in txt_files_map:
        if k in pred_files_map and k in ref_files_map:
            files.append((txt_files_map[k], pred_files_map[k], ref_files_map[k]))


    # txt          <- medical text
    # annotations  <- predictions
    # gold         <- gold standard


    truePositivesExactSpan = 0
    falseNegativesExactSpan = 0
    falsePositivesExactSpan = 0

    truePositivesInexactSpan = 0
    falseNegativesInexactSpan = 0
    falsePositivesInexactSpan = 0

    confusion = [[0] * len(labels) for e in labels]

    confusionMatrixExactSpan = deepcopy(confusion)
    confusionMatrixInexactSpan = deepcopy(confusion)



    for txt, annotations, gold in files:

        # Read predictions and gols standard data
        cnote = Note(format)
        rnote = Note(format)
        cnote.read(txt, annotations)
        rnote.read(txt,        gold)

        referenceSpans = getConceptSpans(rnote.getIOBLabels(), rnote.conlist())
        predictedSpans = getConceptSpans(cnote.getIOBLabels(), cnote.conlist())

        #TO DO: i need to generate a cumulative total accross all of the files
        #modify my functions slightly and have it return the number of true positive and etc...
        #then call generate results

        exactResults =  evaluate(deepcopy(referenceSpans), deepcopy(predictedSpans), exactMatch=True, reportSeperately=False)

        inexactResults =  evaluate(deepcopy(referenceSpans), deepcopy(predictedSpans), exactMatch=False, reportSeperately=False)


        truePositivesExactSpan += exactResults["True Positives"]
        falseNegativesExactSpan += exactResults["False Negatives"]
        falsePositivesExactSpan += exactResults["False Positives"]


        inexactResults = evaluate(deepcopy(referenceSpans), deepcopy(predictedSpans), exactMatch=False, reportSeperately=False)

        truePositivesInexactSpan += inexactResults["True Positives"]
        falseNegativesInexactSpan += inexactResults["False Negatives"]
        falsePositivesInexactSpan += inexactResults["False Positives"]

        MatrixInexactSpan = evaluate(deepcopy(referenceSpans), deepcopy(predictedSpans), exactMatch=False, reportSeperately=True)

        for sublist1, sublist2 in zip(confusionMatrixInexactSpan, MatrixInexactSpan):
            for i,int2 in enumerate(sublist2):
                sublist1[i] += int2

        MatrixExactSpan = evaluate(deepcopy(referenceSpans), deepcopy(predictedSpans), exactMatch=True, reportSeperately=True)

        for sublist1, sublist2 in zip(confusionMatrixExactSpan, MatrixExactSpan):
            for i,int2 in enumerate(sublist2):
                sublist1[i] += int2

    print "\nResults for exact span for concepts together.\n"

    print "True Positives: ", truePositivesExactSpan
    print "False Negatives: ", falseNegativesExactSpan
    print "False Positives: ", falsePositivesExactSpan

    exactSpan = generateResultsForExactSpans(truePositivesExactSpan,
                                 falseNegativesExactSpan,
                                 falsePositivesExactSpan)

    print "Recall: ", exactSpan["Recall"]
    print "Precision: ", exactSpan["Precision"]
    print "F Measure: ", exactSpan["F Score"]

    inexactSpan = generateResultsForExactSpans(truePositivesInexactSpan,
                                 falseNegativesInexactSpan,
                                 falsePositivesInexactSpan)

    print "\nResults for inexact span for concepts together.\n"

    print "True Positives: ", truePositivesInexactSpan
    print "False Negatives: ", falseNegativesInexactSpan
    print "False Positives: ", falsePositivesInexactSpan

    print "Recall: ", inexactSpan["Recall"]
    print "Precision: ", inexactSpan["Precision"]
    print "F Measure: ", inexactSpan["F Score"]

    #TO DO: ENSURE NUMBER OF FP,FN,TP is equal to number of predicted spans
    #TO DO: number of FP, FN, TP is not same between exact and inexact.

    #LEFT OFF HERE. FIX DISPLAY FUNCTION

    displayMatrix(args.output, 'Exact'  , confusionMatrixExactSpan)
    displayMatrix(args.output, 'Inexact', confusionMatrixInexactSpan)


        #print evaluate(deepcopy(referenceSpans), deepcopy(predictedSpans), exactMatch=False, reportSeperately=True)

    return

if __name__ == '__main__':
    main()

