# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 25/05/2021
 Descrizione...: Visualizza contenuto di una tabella sqlite
"""

# Librerie sistema
import os
# Librerie di data base
import sqlite3 
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField
#Import dei moduli interni
from utilita_database import estrae_struttura_tabella_sqlite

class import_export_sqlite_viewer_class(FlaskForm):
    """
        classe per creazione campi all'interno dell'html
    """	    
    e_sqlite = TextField('SQLite DB name:')
    e_sqlite_table_name = TextField('Table name:')        
    b_sqlite_table_viewer = SubmitField('View table')

def sqlite_viewer(p_sqlite_db_name,
                  p_table_name):
    """
       data una tabella sqlite restituisce struttura table in html
    """
    # controllo presenza dei dati in ingresso
    if p_table_name == '' or p_sqlite_db_name == '':
        return 'Please set table name e SQLite db'        
            
    #Apro il DB sqlite        
    v_sqlite_conn = sqlite3.connect(database=p_sqlite_db_name)    
    v_sqlite_cur = v_sqlite_conn.cursor()                
    
    #Carico struttura della tabella
    elenco_colonne = estrae_struttura_tabella_sqlite('1', v_sqlite_cur, p_table_name)                             
    #Carico intestazioni tabella html
    v_html = '<table class="table table-hover sortable"> <thead> <tr>'
    for row in elenco_colonne:
        v_html += '<th>' + row + '</th>' 
    v_html += ' </tr> </thead>'    
                                        
    #Lettura del contenuto della tabella    
    query = estrae_struttura_tabella_sqlite('s', v_sqlite_cur, p_table_name)         
    v_sqlite_cur.execute(query)
    rows = v_sqlite_cur.fetchall()        
    #carico i dati presi dal db dentro il modello tabella
    v_html += '<tbody id="id_my_table">'
    for row in rows:                    
        v_html += '<tr>'
        #carico riga
        for field in row:
            v_html += '<td>' + str(field) + '</td>'         
        # chiusura riga
        v_html += '</tr>'
           
    # chiudo tabella html e connessione a db
    v_html += '</tbody> </table>'     
    v_sqlite_conn.close()   

    # restituisco il risultato
    return v_html                             

# ----------------------------------------
# TEST APPLICAZIONE
# ----------------------------------------
if __name__ == "__main__":    
    print( sqlite_viewer(os.path.normpath('temp\\MGrepTransfer.db'), 'DO_DCTIP') )