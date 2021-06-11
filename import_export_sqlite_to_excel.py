# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 25/05/2021
 Descrizione...: Esporta in excel una tabella contenuta in un db sqlite
"""

# Librerie sistema
import os
# Librerie di data base
import sqlite3 
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, SubmitField, SelectField
# Moduli di progetto
from utilita_database import estrae_struttura_tabella_sqlite

class import_export_sqlite_to_excel_class(FlaskForm):
    """
        classe per creazione campi all'interno dell'html
    """	    
    e_sqlite = TextField('SQLite DB name:')
    e_sqlite_table_name = TextField('Table name:')        
    b_sqlite_table_to_excel = SubmitField('Export to Excel')

def copy_sqlite_to_excel(p_sqlite_db_name, p_sqlite_table_name,p_excel_file):
    """
       Copia una tabella sqlite dentro un file di excel
    """
    #Libreria per export in excel
    from xlsxwriter.workbook import Workbook

    #Apre il DB sqlite (lo apro in modalità classica....non dovrei avere problemi con utf-8)
    v_sqlite_conn = sqlite3.connect(database=p_sqlite_db_name)
    v_sqlite_cur = v_sqlite_conn.cursor()        
            
    #Controllo se la tabella esiste
    query = 'SELECT COUNT(*) FROM ' + p_sqlite_table_name
    try:
        v_sqlite_cur.execute(query)
    except:
        return 'ko','Table in SQLite DB not exists!'        
            
    #Creazione del file excel
    workbook = Workbook(p_excel_file)
    worksheet = workbook.add_worksheet()

    #Estraggo elenco dei campi
    v_struttura = estrae_struttura_tabella_sqlite('1',v_sqlite_cur,p_sqlite_table_name)

    #Carico elenco dei campi nella prima riga del foglio        
    pos = 0
    for i in v_struttura:
        worksheet.write(0, pos, i)
        pos += 1

    #Carico tutte le altre righe della tabella                    
    query = 'SELECT * FROM ' + p_sqlite_table_name        
    v_sqlite_cur.execute(query)
    for i, row in enumerate(v_sqlite_cur):            
        for j,value in enumerate(row):
            worksheet.write(i+1, j, row[j])        
            
    #Chiusura del file e del db
    workbook.close()
    v_sqlite_conn.close()                    
    #Messaggio finale        
    return 'ok','Table export completed!'
    
# ------------------------
# test 
# ------------------------
if __name__ == "__main__":
    v_ok, message = copy_sqlite_to_excel(os.path.normpath('temp\\MGrepTransfer.db'), 
                                        'MA_CCIAA', 
                                        os.path.normpath('temp\\'+'prova.xlsx'))