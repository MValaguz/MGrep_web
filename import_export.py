# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 09/04/2021
 Descrizione...: Programma importazione e esportazione dei dati tra diversi ambienti (da Oracle a SQLite e viceversa, elaborazioni su file Excel)
"""

# Librerie sistema
import sys
import os
# Librerie di data base
import cx_Oracle
import sqlite3 
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError
# Moduli di progetto
from utilita_database import estrae_struttura_tabella_oracle
from utilita_database import estrae_struttura_tabella_sqlite 
from utilita_database import table_exists_sqlite

class import_export_class(FlaskForm):
    """
        classe per creazione campi all'interno dell'html
    """	
    e_server_name = SelectField('Oracle name server:')
    e_schema = SelectField('Oracle schema:', choices = ['SMILE','SMI'])	
    e_sqlite = TextField('SQLite DB name:')

    e_from_oracle_table = TextField('Table name:') 
    e_oracle_where = TextField('Where condition:')
    b_copy_from_oracle_to_sqlite = SubmitField('Copy table from Oracle DB to SQLite:')

def copy_table_oracle_to_sqlite(v_user_db,
                                v_password_db,
                                v_dsn_db,
                                v_table_name,
                                v_table_where,
                                v_sqlite_db_name,
                                v_blob_pathname,
                                v_overwrite): 
    """
       copia una tabella oracle dentro un database sqlite
            v_user_db = utente del database oracle
            v_password_db = password database oracle
            v_dsn_db = nome database oracle
            v_table_name = nome della tabella di oracle
            v_table_where = eventuale where 
            v_sqlite_db_name = nome del database sqlite
            v_blob_pathname = pathname dove verranno caricati eventuali blob presenti in tabella oracle
            v_overwrite = se true indica di sovrascrivere eventuale tabella già presente in sqlite
    """    
    # Metto tutto maiuscolo i parametri nome tabella e where
    v_table_name =str(v_table_name).upper()
    v_table_where =str(v_table_where).upper()

    # Collegamento a Oracle
    try:
        v_oracle_db = cx_Oracle.connect(user=v_user_db, password=v_password_db, dsn=v_dsn_db)        
    except:
        return "ko", "Connecting problems to Oracle DB!"
        
    v_oracle_cursor = v_oracle_db.cursor()    
    # Apre il DB sqlite    
    v_sqlite_conn = sqlite3.connect(database=v_sqlite_db_name)
    # Indico al db di funzionare in modalità byte altrimenti ci sono problemi nel gestire utf-8
    v_sqlite_conn.text_factory = bytes
    v_sqlite_cur = v_sqlite_conn.cursor()
    
    # Se la tabella SQLite esiste ...
    if table_exists_sqlite(v_sqlite_cur, v_table_name):
        # se richiesto di sovrascrivere procedo con la cancellazione...
        if v_overwrite:                            
            # Cancello la tabella se già presente nel db sqlite            
            v_sqlite_cur.execute('DROP TABLE ' + v_table_name)    
        # altrimenti esco con errore
        else:            
            return "ko", "Table in SQLite DB already exist!"
        
    # Conta dei record nella tabella sorgente Oracle
    # Aggiungo la where (solo se caricata)        
    query = 'SELECT COUNT(*) FROM ' + v_table_name        
    if len(v_table_where.split()) > 0:
        query += ' WHERE ' + v_table_where
    try:    
        v_oracle_cursor.execute(query)
    except:
        #errore 
        return "ko", "Oracle table do not exists or errors in 'where' condition!"        
    
    v_total_rows = 0
    for row in v_oracle_cursor:                  
        v_total_rows = row[0]
    # Calcolo 1% che rappresenta lo spostamento della progress bar
    v_rif_percent = 0
    if v_total_rows > 100:
        v_rif_percent = v_total_rows // 100

    # Creo la tabella in ambiente di backup (ottengo lo script di create table)
    query = estrae_struttura_tabella_oracle('c', v_oracle_cursor, v_user_db, v_table_name)    
    v_sqlite_cur.execute(query)

    # Creo una lista con le posizioni dei campi dove si trovano i blob 
    # In pratica un array dove sono segnati le posizioni dei campi
    # Esempio:
    #CREATE TABLE ta_files (
    #  files_nu NUMBER(8,0)   NOT NULL,
    #  modul_do VARCHAR2(1)   NOT NULL,
    #  files_do VARCHAR2(1)   NOT NULL,
    #  filen_co VARCHAR2(200) NOT NULL,
    #  exten_co VARCHAR2(20)  NULL,
    #  files_fi BLOB          NULL,
    #  ....
    #)
    # La lista conterrà un solo elemento con valore 6 indicante la posizione del campo files_fi
    v_posizioni_blob = estrae_struttura_tabella_oracle('b', v_oracle_cursor, v_user_db, v_table_name)
    v_estensione_blob = estrae_struttura_tabella_oracle('e', v_oracle_cursor, v_user_db, v_table_name)

    # Se nella tabella sono presenti dei blob, creo una cartella nel file system dove ci finiranno i blob
    v_message_info = ''
    if v_posizioni_blob:     
        v_message_info = 'Table contained blob data! It was copied in ' + v_blob_pathname + '\\' + v_table_name + '.'
        try:            
            os.mkdir(v_blob_pathname + '\\' + v_table_name)                
        # Se la cartella esiste già errore ed esco
        except:
            # elimino il contenuto della cartella se richiesto di andare sovrascrittura
            if v_overwrite:                
                os.rmdir(v_blob_pathname)
                os.mkdir(v_blob_pathname + '\\' + v_table_name)                
            # errore se non richiesto di sovrascrivere
            else:
                return "ko", "The table contains blob fields! The copy must create the directory " + v_table_name + " but this already exists!"            

        # In questa cartella inserisco un file di testo che riporta le posizioni dei blob. Tale file verrà poi utilizzo nel caso
        # si voglia ricopiare la tabella dentro Oracle
        v_file_allegato = open(v_blob_pathname + '\\' + v_table_name + '\\blob_fields_position.ini','w')
        v_file_allegato.write(str(v_posizioni_blob))
        v_file_allegato.close()                            
                
    # Copia dei dati
    query = estrae_struttura_tabella_oracle('s', v_oracle_cursor, v_user_db, v_table_name) 
    if len(v_table_where.split()) > 0:
        query += ' WHERE ' + v_table_where

    v_insert_base = estrae_struttura_tabella_oracle('i', v_oracle_cursor, v_user_db, v_table_name)         
    v_oracle_cursor.execute(query)        
    v_progress = 0
    v_puntatore_blob = 0
    v_valore_colonna = str()
    for row in v_oracle_cursor:                  
        v_1a_volta = True
        v_insert = v_insert_base            
        for count, column in enumerate(row):                
            if column is None:
                v_valore_colonna = ''
            else:                
                v_valore_colonna = column
                # se la colonna è un blob --> sostituisco il contenuto con quello del puntatore 
                # e scrivo il contenuto della colonna come file separato in directory a parte
                if v_posizioni_blob:                
                    if count+1 in v_posizioni_blob:                    
                        v_puntatore_blob += 1                                                
                        v_file_allegato = open(v_blob_pathname + '\\' + v_table_name + '\\' + str(v_puntatore_blob) + '.zzz','wb')
                        v_file_allegato.write(column.read())
                        v_file_allegato.close()                            
                        v_valore_colonna = str(v_puntatore_blob)                    
                
            # compongo la insert con il contenuto della colonna (da notare il replace del carattere " con apice singolo!)
            v_valore_colonna = str(v_valore_colonna)                    
            if v_1a_volta:                
                v_insert += '"' + v_valore_colonna.replace('"',"'") + '"'
            else:
                v_insert += ',"' + v_valore_colonna.replace('"',"'") + '"'
                
            v_1a_volta = False
        v_insert += ')'        
        v_sqlite_cur.execute(v_insert)    

        # Emetto percentuale di avanzamento ma solo se righe maggiori di 100
        """
        if v_total_rows > 100:
            v_progress += 1
            if v_progress % v_rif_percent == 0:                                    
                self.avanza_progress('Total records to copy: ' + str(v_total_rows))
                #print('Avanzamento scrittura...' + str((v_progress*100//v_total_rows)+1) + '%')                    
        """
    #commit
    v_sqlite_conn.commit()                        
    #chiusura dei cursori
    v_sqlite_conn.close()                    
    v_oracle_cursor.close()   
    
    v_return_message = "Success! Total rows copied " + str(v_total_rows)
    if v_message_info != '':
        v_return_message += ". Notice! " + v_message_info
    return "ok", v_return_message

# ------------------------
# test 
# ------------------------
if __name__ == "__main__":
    v_ok = copy_table_oracle_to_sqlite('SMILE',
                                       'SMILE',
                                       'BACKUP_815',
                                       'OC_CCIAA',
                                       "AZIEN_CO='SMI' AND ESERC_CO='2021'",
                                       os.path.normpath('temp\\'+'TEST.db'),
                                       os.path.normpath('temp'),
                                       True)
    print(v_ok)                  
