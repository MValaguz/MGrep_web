# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 con libreria pyqt5
 Data..........: 06/04/2021
 Descrizione...: Programma per la visualizzazione e gestione dei table space di Oracle
"""

# Librerie sistema
import sys
import re
# Librerie di data base
import cx_Oracle
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError

class table_space_details_class(FlaskForm):
    """
        classe per creazione campi all'interno dell'html
    """	
    b_crea_script = SubmitField('Create script for add space to a tablespace')
    e_risultato = TextField('Result:')	
       
def get_elenco_table_space_details(o_preferenze, e_server_name, e_table_space_name):
    """
        Restituisce in una tupla elenco dei table space
    """    
    try:
        # connessione al DB come amministratore
        v_connection = cx_Oracle.connect(user=o_preferenze.v_oracle_user_sys,
                                         password=o_preferenze.v_oracle_password_sys,
                                         dsn=e_server_name,
                                         mode=cx_Oracle.SYSDBA)            
    except:
        return 'Connection to oracle rejected!'        

    # apro cursori
    v_cursor = v_connection.cursor()
    
    # select table space
    v_select = """SELECT FILE_NAME,
                            BYTES / (1024 * 1024) SPACES,
                            FILE_ID,
                            AUTOEXTENSIBLE,
                            STATUS
                    FROM  DBA_DATA_FILES WHERE TABLESPACE_NAME='""" + e_table_space_name + """'
                    ORDER BY FILE_NAME DESC
                """                    
    # carico i dati
    v_cursor.execute(v_select)        
    
    # intestazioni     
    v_html = '<table class="table table-hover sortable">'
    v_html += """<thead> <tr> 
                        <th>Name DBfile</th> 
                        <th style="text-align:right">MByte</th> 
                        <th style="text-align:right">File ID</th> 
                        <th>Autoextensible</th> 
                        <th>Available</th>                         
                </tr> </thead>"""

    # carico la matrice dei dati 
    v_html += '<tbody id="id_my_table">'
    for row in v_cursor:                    
        v_html += '<tr>'
        
        v_html += '<td>' + str(row[0]) + '</td>'
        v_html += '<td style="text-align:right">' + str(row[1]) + '</td>'
        v_html += '<td style="text-align:right">' + str(row[2]) + '</td>'
        v_html += '<td>' + str(row[3]) + '</td>'
        v_html += '<td>' + str(row[4]) + '</td>'
        
        v_html += '</tr>'
            
    # chiudo tabella html
    v_html += '</tbody> </table>'
            
    # chiudo sessione
    v_cursor.close()
    v_connection.close()
    
    # restituisco tabella
    return v_html    

def crea_script(o_preferenze, e_server_name, e_table_space_name):
    """
        Crea lo script SQL per lanciare la creazione di un nuovo DBFile
    """
    try:
        # connessione al DB come amministratore
        v_connection = cx_Oracle.connect(user=o_preferenze.v_oracle_user_sys,
                                         password=o_preferenze.v_oracle_password_sys,
                                         dsn=e_server_name,
                                         mode=cx_Oracle.SYSDBA)            
    except:
        return 'Connection to oracle rejected!'        

    # apro cursori
    v_cursor = v_connection.cursor()
    
    # select table space
    v_select = """SELECT FILE_NAME, 
                        BYTES / (1024 * 1024) SPACES
                  FROM  DBA_DATA_FILES WHERE TABLESPACE_NAME='T_SMILE'
                  ORDER BY FILE_NAME DESC
               """                    
    
    # carico i dati
    v_cursor.execute(v_select)        
    
    # carica la prima riga
    v_row = v_cursor.fetchone()
    v_nome_primo_dbfile = v_row[0]
    
    # splitto la stringa come nel seguente esempio ['', 'ora03', 'oradata', 'SMIG', 'tsmile94.dbf']
    v_lista = v_nome_primo_dbfile.split('/')
    v_nome_db = v_lista[4]
    v_prefisso = v_nome_db.split('.')[0]
    v_parte_numerica = int(re.search(r'\d+', v_prefisso).group(0))
    v_new_parte_numerica = v_parte_numerica + 1
    v_new_nome_db = v_lista[0]+'/'+v_lista[1]+'/'+v_lista[2]+'/'+v_lista[3]+'/'+v_lista[4].replace(str(v_parte_numerica),str(v_new_parte_numerica))
    # restituisco lo script così generato
    return  "ALTER TABLESPACE " + e_table_space_name + " ADD DATAFILE '" + v_new_nome_db + "' SIZE " + str(v_row[1]) + "M"    