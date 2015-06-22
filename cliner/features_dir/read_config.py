######################################################################
#  CliCon - read_config.py                                           #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Read a configuration file to determine what features     #
#               are available on the system                          #
######################################################################



import os


def enabled_modules():
    """
    enabled_modules()

    @return a dictionary of {name, resource} pairs.

    ex. {'UMLS': None}

    >>> enabled_modules() is not None
    True
    """
    # Open config file
    filename = os.path.join( os.getenv('CLINER_DIR'), 'config.txt' )
    f = open(filename, 'r')

    specs = {}
    module_list = [ 'UMLS' ]


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
