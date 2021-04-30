# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 07/04/2021
 Descrizione...: Programma per la ricerca di spazio occulto occupato dalla tabelle Oracle
"""

# Librerie sistema
import sys
import locale
# Librerie di data base
import cx_Oracle
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError

class table_wasted_class(FlaskForm):
    """
        classe per creazione campi all'interno dell'html
    """	
    e_server_name = SelectField('Oracle name server:')
    e_table_name = TextField('Table name:')        
    b_ricerca = SubmitField("Search table wasted")	    
       
def ricerca_table_wasted(o_preferenze, e_server_name):
    """
        Restituisce una tabella HTML con elenco delle sessioni in blocco        
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

    # select di ricerca
    v_select = """SELECT OWNER,
                            TABLE_NAME,
                            ROUND((BLOCKS * 8)/1000,0) "SIZE_MBYTE",
                            ROUND((NUM_ROWS * AVG_ROW_LEN / 1024)/1000, 0) "ACTUAL_DATA_MBYTE",
                        (ROUND((BLOCKS * 8)/1000,0) - ROUND((NUM_ROWS * AVG_ROW_LEN / 1024)/1000, 0)) "WASTED_MBYTE"
                    FROM   DBA_TABLES
                    WHERE (ROUND((BLOCKS * 8)/1000,0) - ROUND((NUM_ROWS * AVG_ROW_LEN / 1024)/1000, 0)) > 0
                    AND OWNER <> 'SYS'                    
                    ORDER BY 5 DESC
                """        
    
    # carico tutte le righe in una lista
    v_cursor.execute(v_select)       
    matrice_dati = v_cursor.fetchall()                    
    
    # chiudo sessione
    v_cursor.close()
    v_connection.close()

    # intestazioni     
    v_html = '<table class="table table-hover sortable">'
    v_html += '<thead> <tr> <th>Owner</th> <th>Table name</th> <th style="text-align:right">Total size (MByte)</th> <th style="text-align:right">Used size (MByte)</th> <th style="text-align:right">Wasted size (MByte)</th> <th style="text-align:center">Create script</th> </tr> </thead>'    
                            
    # carico la matrice dei dati
    v_html += '<tbody id="id_my_table">'
    v_totale = 0
    for row in matrice_dati:                    
        # apertura riga
        v_html += '<tr>'
        
        v_html += '<td>' + str(row[0]) + '</td>'    
        v_html += '<td>' + str(row[1]) + '</td>'    
        v_html += '<td style="text-align:right">' + str(row[2]) + '</td>'    
        v_html += '<td style="text-align:right">' + str(row[3]) + '</td>'    
        v_html += '<td style="text-align:right">' + str(row[4]) + '</td>'    

        # nel pulsante di kill session annego il rif alla pagina che killa le sessioni con i seguenti parametri: server, sid e numero di serie
        v_html += '<td align="center">  <a href="table_wasted_script?p_server='+e_server_name+'&p_schema='+str(row[0])+'&p_table_name='+str(row[1])+'"> <i class="fas fa-scroll"> </i> </a> </td>'            
        
        # chiusura riga
        v_html += '</tr>'

        # row[4] è la colonna che contiene il valore di spazio occulto
        v_totale += row[4]
            
    # chiudo tabella html
    v_html += '</tbody> </table>'

    # imposto la stringa del totale di spazio occulto
    v_text_totale = ''
    if v_totale > 0:            
        v_text_totale = '. Total space wasted GByte: ' + str(locale.format_string('%.2f', v_totale/1000, grouping=True) )
    
    # restituisco la tabella html e il suo totale
    return v_html, v_text_totale

def create_script(o_preferenze, e_server_name, e_schema, e_table_name):
    """
        Crea lo script SQL per lanciare la creazione di un nuovo DBFile
    """   
    v_script = 'ALTER TABLE ' + e_schema + '.' + e_table_name + ' MOVE'
        
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
    v_select = """SELECT INDEX_NAME, TABLESPACE_NAME 
                    FROM   DBA_INDEXES 
                    WHERE  OWNER = '""" + e_schema + """'
                    AND  TABLE_NAME= '""" + e_table_name + """'
                    AND  INDEX_TYPE='NORMAL' 
                    ORDER BY INDEX_NAME
                """        
    
    # carico i dati              
    v_cursor.execute(v_select)        
    v_rows = v_cursor.fetchall()
    
    # chiudo sessione
    v_cursor.close()
    v_connection.close()
    
    # compongo il resto dello script con il nome degli indici
    for v_row in v_rows:
        v_script = v_script + '/ <br> ALTER INDEX ' + e_schema + '.' + v_row[0] + ' REBUILD'
                
    return v_script