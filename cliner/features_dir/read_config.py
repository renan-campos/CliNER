######################################################################
#  CliCon - read_config.py                                           #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Read a configuration file to determine what features     #
#               are available on the system                          #
######################################################################



import os



def back(path):
    return os.path.dirname(path)



#
# enabled_modules
#
# @return dictionary of (name,resource path) pairs.
#
#   ex. {'UMLS': None, 'GENIA': 'genia/geniatagger-3.0.1/geniatagger'}
#
def enabled_modules():

    # Open config file
    BASE_DIR = back(back(__file__))
    filename = os.path.join( BASE_DIR, 'config.txt' )
    f = open(filename, 'r')

    specs = {}
    module_list = [ 'GENIA', 'UMLS' ]


    for line in f.readlines():
        words = line.split()
        if words:

            # Modules
            if words[0] in module_list:
                if words[1] == 'None':
                    specs[words[0]] = None
                else:
                    specs[words[0]] = words[1]

    return specs



# Read from config file when module is imported
print enabled_modules()
