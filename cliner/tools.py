######################################################################
#  CliNER - tools.py                                                 #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: General purpose tools (used mostly by model.py)          #
######################################################################




def flatten(list_of_lists):

    '''
    flatten()

    Purpose: Given a list of lists, flatten one level deep

    @param list_of_lists. <list-of-lists> of objects.
    @return               <list> of objects (AKA flattened one level)

    >>> flatten([['a','b','c'],['d','e'],['f','g','h']])
    ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    '''

    return [item for sublist in list_of_lists for item in sublist]




def save_list_structure(list_of_lists):

    '''
    save_list_structure()

    Purpose: Given a list of lists, save way to recover structure from flattended

    @param list_of_lists. <list-of-lists> of objects.
    @return               <list> of indices, where each index refers to the
                                 beginning of a line in the orig list-of-lists

    >>> save_list_structure([['a','b','c'],['d','e'],['f','g','h']])
    [3, 5, 8]
    '''

    offsets = [ len(sublist) for sublist in list_of_lists ]
    for i in range(1, len(offsets)):
        offsets[i] += offsets[i-1]

    return offsets




def reconstruct_list(flat_list, offsets):

    '''
    save_list_structure()

    Purpose: This undoes a list flattening. Uses value from save_list_structure()

    @param flat_list. <list> of objects
    @param offsets    <list> of indices, where each index refers to the
                                 beginning of a line in the orig list-of-lists
    @return           <list-of-lists> of objects (the original structure)

    >>> reconstruct_list(['a','b','c','d','e','f','g','h'], [3,5,8])
    [['a', 'b', 'c'], ['d', 'e'], ['f', 'g', 'h']]
    '''

    return [ flat_list[i:j] for i, j in zip([0] + offsets, offsets)]

