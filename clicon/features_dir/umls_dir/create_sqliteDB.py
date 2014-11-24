#database.py creates a .db file for performing umls searches. 
import sqlite3  
import os
import sys
import os

def create_db(): 
    
    print "\ncreating umls.db" 
    #connect to the .db file we are creating. 
    db_path = os.path.join(os.environ['CLICON_DIR'],'umls_tables/umls.db')
    conn = sqlite3.connect( db_path ) 
    conn.text_factory = str 

    print "opening files" 
    #load data in files.

    try:
        mrsty_path = os.path.join(os.environ['CLICON_DIR'],'umls_tables/MRSTY')
        MRSTY_TABLE = open( mrsty_path, "r" )
    except IOError:
        print "\nNo file to use for creating MRSTY table\n" 
        conn.close() 
        sys.exit() 

    try:
        mrcon_path = os.path.join(os.environ['CLICON_DIR'],'umls_tables/MRCON')
        MRCON_TABLE = open( mrcon_path , "r" ) 
    except IOError:
        print "\nNo file to use for creating MRCON table\n" 
        conn.close() 
        sys.exit() 

    try:
        mrrel_path = os.path.join(os.environ['CLICON_DIR'],'umls_tables/MRREL')
        MRREL_TABLE = open( mrrel_path , "r" )
    except IOError:
        print "\nNo file to use for creating MRREL table\n"
        conn.close()
        sys.exit()

    try:
        lrabr_path = os.path.join(os.environ['CLICON_DIR'],'umls_tables/LRABR')
        LRABR_TABLE = open( lrabr_path , "r" )
    except IOError:
        print "\nNo file to use for creating LRABR table\n"
        conn.close()
        sys.exit()

    print "reading files"

    MRSTY_TABLE = MRSTY_TABLE.read() 
    MRSTY_TABLE = MRSTY_TABLE.split('\n')

    MRCON_TABLE = MRCON_TABLE.read()  
    MRCON_TABLE = MRCON_TABLE.split( '\n' ) 

    MRREL_TABLE = MRREL_TABLE.read() 
    MRREL_TABLE = MRREL_TABLE.split( '\n' ) 

    LRABR_TABLE = LRABR_TABLE.read()
    LRABR_TABLE = LRABR_TABLE.split( '\n' )

    #data that will be inserted into tables. 
    
   
    MRTSY_DATA = [] 
    MRCON_DATA = [] 
    MRREL_DATA = [] 
  

    LRABR_DATA = []

    c = conn.cursor() 

    print "parsing files" 

    #parse and store the data from the files. 

   
    for line in MRSTY_TABLE: 
        MRTSY_DATA.append( tuple(line.split('|')) )
    for line in MRCON_TABLE:
        MRCON_DATA.append( tuple(line.split('|')) )
    for line in MRREL_TABLE:
        MRREL_DATA.append( tuple(line.split('|')) )
    

    for line in LRABR_TABLE:
        LRABR_DATA.append( tuple(line.split('|')) )

    print "creating tables" 

    #create tables. 
   
    c.execute( "CREATE TABLE MRCON( CUI, LAT, TS, LUI, STT, SUI, STR, LRL, EMPTY ) ;" )
    c.execute( "CREATE TABLE MRSTY( CUI, TUI, STY, EMPTY ) ;" )  
    c.execute( "CREATE TABLE MRREL( CUI1, REL, CUI2, RELA, SAB, SL, MG, EMPTY ) ;" ) 
   

    c.execute( "CREATE TABLE LRABR( EUI1, ABR, TYPE, EUI2, STR, EMPTY ) ;" )

    print "inserting data" 

    #insert data onto database
   
    for line in MRCON_DATA:
        try:
            c.execute( "INSERT INTO MRCON( CUI, LAT, TS, LUI, STT, SUI, STR, LRL, EMPTY ) values ( ?, ?, ? ,?, ?,?,?,?,?);", line )
        except sqlite3.ProgrammingError:
            continue
    for line in MRTSY_DATA:
        try:
            c.execute( "INSERT INTO MRSTY( CUI, TUI, STY, EMPTY) values( ?, ?, ?, ?)" , line )  
        except sqlite3.ProgrammingError:
            continue 
    for line in MRREL_DATA:
        try:
            c.execute( "INSERT INTO MRREL(  CUI1, REL, CUI2, RELA, SAB, SL, MG, EMPTY ) values( ?, ?, ?, ?,?, ? ,? ,? )" , line )
        except sqlite3.ProgrammingError:
            continue 
   
    for line in LRABR_DATA:
        try:
            c.execute( "INSERT INTO LRABR( EUI1, ABR, TYPE, EUI2, STR, EMPTY ) values ( ?, ?, ?, ?, ?, ?)", line )
        except sqlite3.ProgrammingError:
            continue

    print "creating indices" 

    #create indices for faster queries
    
   
    c.execute( "CREATE INDEX mrsty_cui_map ON MRSTY(CUI)")  
    c.execute( "CREATE INDEX mrcon_str_map ON MRCON(STR)")  
    c.execute( "CREATE INDEX mrcon_cui_map ON MRCON(CUI)")
    c.execute( "CREATE INDEX mrrel_cui2_map ON MRREL( CUI2 )" )
    c.execute( "CREATE INDEX mrrel_cui1_map on MRREL( CUI1 ) " ) 
    c.execute( "CREATE INDEX mrrel_rel_map on MRREL( REL )" ) 
    c.execute( "CREATE INDEX lrabr_abr_map on LRABR(ABR)")
    c.execute( "CREATE INDEX lrabr_str_map on LRABR(STR)")

    #save changes to .db
    conn.commit()

    print "\nsqlite database created" 

    #close connection
    conn.close()

