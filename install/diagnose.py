######################################################################
#  CliNER - diagnose.py                                              #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Determine if user is missing anything for installation.  #
######################################################################


import os

from dependencies.status_report import check_python_dependencies_installed
from dependencies.status_report import display_status
from dependencies.status_report import auxiliary as dependencies_auxiliary
from dependencies.status_report import required  as dependencies_required
from dependencies.status_report import nltk_data as dependencies_nltk_data



def main():


    # 2. Python dependencies
    status = check_python_dependencies_installed()
    if all(status):
        print '\ngood: all Python dependencies installed'
    if status[0] == False:
        print '\nWARNING: Auxillary Python dependencies NOT installed'
        display_status(dependencies_auxiliary)
    if status[1] == False:
        print '\nERROR: Required Python dependencies NOT installed'
        display_status(dependencies_required)
    if status[2] == False:
        print '\nERROR: Required nltk data NOT downloaded'
        display_status(dependencies_nltk_data)
    print


    # 3. GENIA Tagger (optional)


    # 4. UMLS tables (optional)




if __name__ == '__main__':
    main()
