# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 15/03/2021
 Descrizione...: Programma per la ricerca di stringe in files e oggetti di database Oracle. Restituisce una tabella in formato html.
"""

# Librerie sistema
import sys
import os
# Librerie di data base
import cx_Oracle
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError

class search_string_class(FlaskForm):
    """
        classe per creazione campi all'interno dell'html
    """
    e_stringa1 = TextField('Search string1')
    e_stringa2 = TextField('Search string2')
    c_flsearch = BooleanField('Execute search in folder')
    e_pathname = TextField('Folder name')
    e_filter = TextField('File filter')
    e_excludepath = TextField('Exclude directories')
    c_dbsearch = BooleanField('Execute search in OracleDB')
    e_dboracle1 = TextField('Oracle connection1')
    e_dboracle2 = TextField('Oracle connection2')
    c_icomsearch = BooleanField('Execute search in ICOM')

    b_search = SubmitField("Start search")

def carica_default(p_form, p_preferenze):
    """
       carica le preferenze p_preferenze nei campi di p_form
    """
    p_form.e_stringa1.data=p_preferenze.stringa1
    p_form.e_stringa2.data=p_preferenze.stringa2
    p_form.e_pathname.data=p_preferenze.pathname
    p_form.e_excludepath.data=p_preferenze.excludepath
    p_form.e_filter.data=p_preferenze.filter
    p_form.e_dboracle1.data=p_preferenze.dboracle1
    p_form.e_dboracle2.data=p_preferenze.dboracle2

    p_form.c_flsearch.data=p_preferenze.flsearch
    p_form.c_dbsearch.data=p_preferenze.dbsearch
    p_form.c_icomsearch.data=p_preferenze.icomsearch

def ricerca_stringa_in_file(v_root_node,
                            v_string1,
                            v_string2,                            
                            v_filter,
                            v_exclude,
                            v_risultati):
    """
        ricerca stringa in file
    """    
    # ricavo una tupla contenente i filtri di ricerca separati
    v_filtri_ricerca = v_filter.split(',')

    # ricavo una tupla contenente le directory da escludere
    v_exclude_ricerca = v_exclude.split(',')
        
    # lista dei files contenuti nella directory (os.walk restituisce le tuple di tutte le directory partendo dal punto di root)        
    for root, dirs, files in os.walk(v_root_node):
        # elimino dall'albero delle dir quelle che vanno escluse!
        # Se la stessa dir fosse presente anche ai livelli successivi, viene eliminata anche da li
        for i in range(0, len(v_exclude_ricerca)):
            if v_exclude_ricerca[i] in dirs:
                dirs.remove(v_exclude_ricerca[i])
        # scorro le tuple dei nomi dentro tupla dei files            
        for name in files:
            # partendo dalla directory e dal nome file, uso la funzione join per avere il nome del file completo
            v_file_name = os.path.join(root, name)
            # stesso discorso istruzione precedente per quanto riguarda la directory (viene poi salvata nel file risultato)
            v_dir = os.path.join(root)
            v_dir_is_valid = True
            # stesso discorso istruzione precedente per quanto riguarda il file (viene poi salvata nel file risultato)
            v_file = os.path.join(name)
            # se presenti i filtri di ricerca --> controllo che il file corrisponda alla lista indicata
            v_file_is_valid = False
            if v_filter != '':
                for i in range(0, len(v_filtri_ricerca)):
                    if v_file.find(v_filtri_ricerca[i]) > 0:
                        v_file_is_valid = True
                        break
            else:
                v_file_is_valid = True
            # se nome del file è valido
            if v_dir_is_valid and v_file_is_valid:
                # apertura del file (in modo binario! la documentazione dice che la modalita rb vale solo per sistema MS-WIN)
                # viene tentata l'apertura tramite una try perché tra il momento di creazione della lista dei file da
                # elaborare e l'effettiva lettura, il file potrebbe essere stato eliminato
                try:
                    f_input = open(v_file_name,'rb')  # Con il passaggio a python3.6 non funzionava più correttamente
                    v_file_is_open = True
                except:
                    print('File ' + v_file_name + ' non trovato!')
                    v_file_is_open = False
                if v_file_is_open:
                    # estraggo dal nome file l'estensione e il nome (servono per scrivere il csv)
                    v_only_file_name, v_only_file_extension = os.path.splitext(v_file)
                    # Lettura di tutto il file  
                    try:
                        f_contenuto = f_input.read().upper()
                    except MemoryError:
                        return('File ' + v_file_name + ' is too big! Stopped!')
                        
                    # utente ha richiesto di ricercare due stringhe in modalita AND
                    if len(v_string1) > 0 and len(v_string2) > 0:
                        if f_contenuto.find(bytes(v_string1.upper(), encoding='latin-1')) >= 0 and f_contenuto.find(
                                bytes(v_string2.upper(), encoding='latin-1')) >= 0:
                            v_risultati.append( ('File', v_file_name) )                                                            
                    # utente ha richiesto di ricercare solo una stringa, la prima
                    elif len(v_string1) > 0:
                        if f_contenuto.find(bytes(v_string1.upper(), encoding='latin-1')) >= 0:
                            v_risultati.append( ('File',v_file_name) )                             
                    # utente ha richiesto di ricercare solo una stringa, la seconda
                    elif len(v_string2) > 0:
                        if f_contenuto.find(bytes(v_string2.upper(), encoding='latin-1')) >= 0:
                            v_risultati.append( ('File',v_file_name) )                                                            
                    # chiudo il file
                    f_input.close()    
    
    return 'Ok'

def ricerca_stringa_in_db(v_db,
                          v_string1,
                          v_string2,                            
                          v_risultati):
    """
        ricerca stringa in dbase
    """
    v_abort = False
    try:
        v_connection = cx_Oracle.connect(v_db)        
    except:
        return('Connection to oracle rejected. Search will skipped!')                    

    # apro cursori
    v_cursor = v_connection.cursor()
    v_cursor_det = v_connection.cursor()

    ##############################################################
    # ricerca all'interno di procedure, funzioni, package e trigger
    ##############################################################
    v_cursor.execute("SELECT DISTINCT NAME,TYPE FROM USER_SOURCE WHERE TYPE IN ('PROCEDURE','PACKAGE','TRIGGER','FUNCTION') ORDER BY TYPE, NAME")    
    for result in v_cursor:
        v_c_name = result[0]
        v_c_type = result[1]            
        # lettura del sorgente (di fatto una lettura di dettaglio di quanto presente nel cursore di partenza                
        # in data 20/12/2018 si è dovuta aggiungere la conversione in ASCII in quanto nel pkg CG_FATTURA_ELETTRONICA risultano annegati caratteri che python non riesce a leggere
        v_cursor_det.prepare("SELECT Convert(TEXT,'US7ASCII') FROM USER_SOURCE WHERE NAME=:p_name ORDER BY LINE")
        v_cursor_det.execute(None, {'p_name': v_c_name})
        # il sorgente finisce dentro la stringa v_sorgente
        v_sorgente = ''
        for result in v_cursor_det:
            v_sorgente = v_sorgente + v_sorgente.join(result)

        v_sorgente = v_sorgente.upper()
        # utente ha richiesto di ricercare due stringhe in modalita AND
        if len(v_string1) > 0 and len(v_string2) > 0:
            if v_sorgente.find(v_string1.upper()) >= 0 and v_sorgente.find(v_string2.upper()) >= 0:                
                v_risultati.append( (v_c_type,v_c_name) )                
        # utente ha richiesto di ricercare solo una stringa, la prima
        elif len(v_string1) > 0:
            if v_sorgente.find(v_string1.upper()) >= 0:
                v_risultati.append( (v_c_type, v_c_name) )                
        # utente ha richiesto di ricercare solo una stringa, la seconda
        elif len(v_string2) > 0:
            if v_sorgente.find(v_string2.upper()) >= 0:                
                v_risultati.append( (v_c_type, v_c_name) )                

    ####################################################
    # ricerca all'interno della definizione delle tabelle
    ####################################################    
    v_owner = v_db[0:v_db.find('/')]
    v_cursor.execute("SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = " + "'" + v_owner + "'" + " ORDER BY TABLE_NAME")    
    for result in v_cursor:
        # nome della tabella
        v_c_name = result[0]
        v_c_type = 'TABLE'
        # preparazione select per la lettura delle colonne e relativi commenti di tabella. Gli spazi sono stati inseriti in quanto il sorgente estratto risultava come unica riga e la ricerca successiva non teneva conto di eventuali separatori
        v_cursor_det.prepare("SELECT :p_name FROM DUAL UNION SELECT ' ' || A.COLUMN_NAME || ' ' || B.COMMENTS FROM ALL_TAB_COLUMNS A, ALL_COL_COMMENTS B WHERE A.OWNER=:p_owner AND A.TABLE_NAME = :p_name AND A.OWNER=B.OWNER AND A.TABLE_NAME=B.TABLE_NAME AND A.COLUMN_NAME=B.COLUMN_NAME")
        v_cursor_det.execute(None, {'p_owner': v_owner, 'p_name': v_c_name})
        # il sorgente finisce dentro la stringa v_sorgente
        v_sorgente = ''
        for result in v_cursor_det:
            v_sorgente = v_sorgente + v_sorgente.join(result)

        v_sorgente = v_sorgente.upper()

        # utente ha richiesto di ricercare due stringhe in modalita AND
        if len(v_string1) > 0 and len(v_string2) > 0:
            if v_sorgente.find(v_string1.upper()) >= 0 and v_sorgente.find(v_string2.upper()) >= 0:
                v_risultati.append( (v_c_type, v_c_name) )                
        # utente ha richiesto di ricercare solo una stringa, la prima
        elif len(v_string1) > 0:
            if v_sorgente.find(v_string1.upper()) >= 0:
                v_risultati.append( (v_c_type, v_c_name) )                
        # utente ha richiesto di ricercare solo una stringa, la seconda
        elif len(v_string2) > 0:
            if v_sorgente.find(v_string2.upper()) >= 0:                
                v_risultati.append( (v_c_type, v_c_name) )                

    ##################################################
    # ricerca all'interno della definizione delle viste
    ##################################################    
    v_owner = v_db[0:v_db.find('/')]
    v_cursor.execute("SELECT VIEW_NAME FROM ALL_VIEWS WHERE OWNER = " + "'" + v_owner + "'" + " ORDER BY VIEW_NAME")
    for result in v_cursor:
        # nome della tabella
        v_c_name = result[0]
        v_c_type = 'VIEW'
        # preparazione select per la lettura delle colonne e relativi commenti di tabella
        v_cursor_det.prepare("SELECT :p_name FROM DUAL UNION SELECT ' ' || A.COLUMN_NAME || ' ' || B.COMMENTS FROM ALL_TAB_COLUMNS A, ALL_COL_COMMENTS B WHERE A.OWNER=:p_owner AND A.TABLE_NAME = :p_name AND A.OWNER=B.OWNER AND A.TABLE_NAME=B.TABLE_NAME AND A.COLUMN_NAME=B.COLUMN_NAME")
        v_cursor_det.execute(None, {'p_owner': v_owner, 'p_name': v_c_name})
        # il sorgente finisce dentro la stringa v_sorgente
        v_sorgente = ''
        for result in v_cursor_det:
            v_sorgente = v_sorgente + v_sorgente.join(result)

        v_sorgente = v_sorgente.upper()
        # utente ha richiesto di ricercare due stringhe in modalita AND
        if len(v_string1) > 0 and len(v_string2) > 0:
            if v_sorgente.find(v_string1.upper()) >= 0 and v_sorgente.find(v_string2.upper()) >= 0:
                v_risultati.append( (v_c_type, v_c_name) )                
        # utente ha richiesto di ricercare solo una stringa, la prima
        elif len(v_string1) > 0:
            if v_sorgente.find(v_string1.upper()) >= 0:
                v_risultati.append( (v_c_type, v_c_name) )                
        # utente ha richiesto di ricercare solo una stringa, la seconda
        elif len(v_string2) > 0:
            if v_sorgente.find(v_string2.upper()) >= 0:
                v_risultati.append( (v_c_type, v_c_name) )                

        # preparazione select per la lettura del sorgente della vista
        v_cursor_det.prepare("SELECT TEXT FROM ALL_VIEWS WHERE VIEW_NAME=:p_name")
        v_cursor_det.execute(None, {'p_name': v_c_name})
        # il sorgente finisce dentro la stringa v_sorgente
        v_sorgente = ''
        for result in v_cursor_det:
            v_sorgente = v_sorgente + v_sorgente.join(result)

        v_sorgente = v_sorgente.upper()
        # utente ha richiesto di ricercare due stringhe in modalita AND
        if len(v_string1) > 0 and len(v_string2) > 0:
            if v_sorgente.find(v_string1.upper()) >= 0 and v_sorgente.find(v_string2.upper()) >= 0:
                v_risultati.append( (v_c_type, v_c_name) )                
        # utente ha richiesto di ricercare solo una stringa, la prima
        elif len(v_string1) > 0:
            if v_sorgente.find(v_string1.upper()) >= 0:
                v_risultati.append( (v_c_type, v_c_name) )                
        # utente ha richiesto di ricercare solo una stringa, la seconda
        elif len(v_string2) > 0:
            if v_sorgente.find(v_string2.upper()) >= 0:
                v_risultati.append( (v_c_type, v_c_name) )                

    ###########################################################################################
    # ricerca dentro la UT_LOV (tabella delle liste di valori)...ma solo se connessi al DB SMILE
    ###########################################################################################    
    if v_db.upper().find('SMILE') >= 0:
        try:                    
            if len(v_string1) > 0 and len(v_string2) > 0:
                # lettura di UT_LOV
                v_cursor_det.prepare("""SELECT NAME_CO
                                        FROM   UT_LOV
                                        WHERE  (SEL01_CO || SEL02_CO || SEL03_CO || SEL04_CO || SEL05_CO ||
                                                SEL06_CO || SEL07_CO || SEL08_CO || SEL09_CO || SEL10_CO ||
                                                FROM_CO  || WHERE_CO || ORDER_CO)
                                                LIKE '%' || UPPER(:p_string1) || '%' AND
                                                (SEL01_CO || SEL02_CO || SEL03_CO || SEL04_CO || SEL05_CO ||
                                                SEL06_CO || SEL07_CO || SEL08_CO || SEL09_CO || SEL10_CO ||
                                                FROM_CO  || WHERE_CO || ORDER_CO)
                                                LIKE '%' || UPPER(:p_string2) || '%'
                                    """)
                v_cursor_det.execute(None, {'p_string1': v_string1, 'p_string2': v_string2})
                for result in v_cursor_det:
                    v_c_lov_name = result[0]
                    v_risultati.append( (' UT_LOV', v_c_lov_name) )                    
            elif len(v_string1) > 0:
                # lettura di UT_LOV
                v_cursor_det.prepare("""SELECT NAME_CO
                                        FROM   UT_LOV
                                        WHERE  (SEL01_CO || SEL02_CO || SEL03_CO || SEL04_CO || SEL05_CO ||
                                                SEL06_CO || SEL07_CO || SEL08_CO || SEL09_CO || SEL10_CO ||
                                                FROM_CO  || WHERE_CO || ORDER_CO)
                                                LIKE '%' || UPPER(:p_string1) || '%'
                                    """)
                v_cursor_det.execute(None, {'p_string1': v_string1})
                for result in v_cursor_det:
                    v_c_lov_name = result[0]
                    v_risultati.append( ('UT_LOV', v_c_lov_name) )                    
        except:
            pass
        
        ###########################################################################################
        # ricerca dentro la ALL_SCHEDULER_JOBS (tabella dei job schedulati)
        ###########################################################################################
        if v_db.upper().find('SMILE') >= 0:
            try:
                if len(v_string1) > 0 and len(v_string2) > 0:
                    # lettura di UT_LOV
                    v_cursor_det.prepare("""SELECT JOB_NAME
                                            FROM   ALL_SCHEDULER_JOBS
                                            WHERE  UPPER(JOB_ACTION) LIKE '%' || UPPER(:p_string1) || '%' 
                                                AND  UPPER(JOB_ACTION) LIKE '%' || UPPER(:p_string2) || '%'
                                        """)
                    v_cursor_det.execute(None, {'p_string1': v_string1, 'p_string2': v_string2})
                    for result in v_cursor_det:
                        v_c_lov_name = result[0]
                        v_risultati.append( ('ALL_SCHEDULER_JOBS', v_c_lov_name) )                        
                elif len(v_string1) > 0:
                    # lettura di UT_LOV                            
                    v_cursor_det.prepare("""SELECT JOB_NAME
                                            FROM   ALL_SCHEDULER_JOBS
                                            WHERE  UPPER(JOB_ACTION) LIKE '%' || UPPER(:p_string1) || '%'
                                        """)
                    v_cursor_det.execute(None, {'p_string1': v_string1})
                    for result in v_cursor_det:
                        v_c_lov_name = result[0]
                        v_risultati.append( ('ALL_SCHEDULER_JOBS', v_c_lov_name) )                        
            except:
                pass                

    # chiusura cursori e connessione DB
    v_cursor_det.close()
    v_cursor.close()
    v_connection.close()    
    
    return 'Ok'

def ricerca_stringa_in_icom(v_string1,
                            v_string2,                            
                            v_risultati):
    """
        ricerca stringa in sorgenti ICOM-UNIFACE
    """    
    try:
        v_connection = cx_Oracle.connect('icom_ng_source/icom_ng_source@uniface')       
    except:
        return('Connection rejected! Search in ICOM-UNIFACE will skipped!')        
    
    # apro cursori
    v_cursor = v_connection.cursor()
    v_cursor_det = v_connection.cursor()
    
    # eseguo la ricerca con apposita funzione
    v_cursor.execute('SELECT rep_search_function(:string1,:string2) FROM dual',{'string1' : v_string1 , 'string2' : v_string2})
    for result in v_cursor:
        if result[0] is not None:
            v_lista  = result[0].split(',')
            for i in v_lista:
                # carico tabella risultati
                v_risultati.append(('ICOM souce',i))

    # chiusura cursori e connessione DB
    v_cursor.close()
    v_connection.close()    
    
    return 'Ok'
       
def ricerca_stringhe(p_form):
    """
        Esegue la ricerca delle stringhe
    """
    # controlli iniziali
    if p_form.e_stringa1.data == '' and p_form.e_stringa2.data == '':
        return "Insert string1 or string2",""

    if not p_form.c_flsearch.data and not p_form.c_dbsearch.data and not p_form.c_icomsearch.data:
        return('Select execute search in Folder or DB or ICOM'),""
        
    if p_form.c_flsearch.data and p_form.e_pathname.data == '':
        return('Please enter a folder name'),""

    if p_form.c_dbsearch.data and p_form.e_dboracle1.data == '' and p_form.e_dboracle2.data == '':
        return('Please enter a DB name'),""

    # richiama la ricerca nel file system se presente file system                
    v_risultati = []
    v_ok = 'Ok'
    if p_form.c_flsearch.data:
        v_ok = ricerca_stringa_in_file(p_form.e_pathname.data,
                                       p_form.e_stringa1.data,
                                       p_form.e_stringa2.data,                                       
                                       p_form.e_filter.data,
                                       p_form.e_excludepath.data,
                                       v_risultati)

    # se presente ricerco nei sorgenti DB della connessione1
    if p_form.c_dbsearch.data and p_form.e_dboracle1.data != '' and v_ok == 'Ok':
        v_ok = ricerca_stringa_in_db(p_form.e_dboracle1.data,
                                     p_form.e_stringa1.data,
                                     p_form.e_stringa2.data,                                            
                                     v_risultati)

    # se presente ricerco nei sorgenti DB della connessione2
    if p_form.c_dbsearch.data and p_form.e_dboracle2.data != '' and v_ok == 'Ok': 
        v_ok = ricerca_stringa_in_db(p_form.e_dboracle2.data,
                                     p_form.e_stringa1.data,
                                     p_form.e_stringa2.data,                                            
                                     v_risultati)

    # eseguo la ricerca nei sorgenti di UNIFACE-ICOM (utente e password di collegamento sono fisse in procedura!)
    if p_form.c_icomsearch.data and v_ok == 'Ok':
        v_ok = ricerca_stringa_in_icom(p_form.e_stringa1.data,
                                       p_form.e_stringa2.data,                                            
                                       v_risultati)
      
    # se tutto ok restituisco una tabella html
    v_html = ''
    if v_ok == 'Ok':        
        # intestazioni (la classe sortable funziona solo se nella pagina html si è inserito lo specifico plugin)
        v_html  = '<div <h1 class="h2">Result</h1> </div>'        
        v_html += '<table class="table table-hover sortable">'      
        v_html += '<thead> <tr> <th>Type</th> <th>Name</th> </tr> </thead>'    
                            
        # carico la matrice dei dati
        v_html += '<tbody id="id_my_table">'
        for row in v_risultati:                    
            # apertura riga
            v_html += '<tr>'
        
            v_html += '<td>' + str(row[0]) + '</td>'    
            v_html += '<td>' + str(row[1]) + '</td>'    
        
            # chiusura riga
            v_html += '</tr>'
            
        # chiudo tabella html
        v_html += '</tbody> </table>'        
        
    # fine con o senza errore
    return v_ok, v_html

# ----------------------------------------
# TEST APPLICAZIONE
# ----------------------------------------
if __name__ == "__main__":         
    # test ricerca in file
    """    
    v_risultati = []   
    v_ok = ricerca_stringa_in_file('W:\\source\\MA-Magazzino\\Sviluppo\\',
                                   'MA_DIZIO',
                                   '',                                       
                                   '.fmb,.rdf',
                                   '',
                                   v_risultati)
    print(v_risultati)
    """
    """
    # test ricerca in db
    v_risultati = []
    v_ok = ricerca_stringa_in_db('SMILE/SMILE@BACKUP_815',
                                 'MA_DIZIO',
                                 '',                                            
                                  v_risultati)
    print(v_risultati)
    """
    # test ricerca in icom
    v_risultati = []
    v_ok = ricerca_stringa_in_icom('MA_PRAGE',
                                   '',                                            
                                   v_risultati)    
    print(v_risultati)