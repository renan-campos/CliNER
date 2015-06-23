
import doctest

import os, sys
home = os.path.join( os.getenv('CLINER_DIR') , 'cliner' )
if home not in sys.path: sys.path.append(home)



def main():

    import notes.note
    doctest.testmod(notes.note)

    import notes.note_i2b2
    doctest.testmod(notes.note_i2b2)
    
    import notes.note_xml
    doctest.testmod(notes.note_xml)
    
    import notes.note_semeval
    doctest.testmod(notes.note_semeval)
    
    import notes.utilities_for_notes
    doctest.testmod(notes.utilities_for_notes)
    


if __name__ == '__main__':
    main()
