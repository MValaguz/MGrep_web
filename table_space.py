# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 con libreria pyqt5
 Data..........: 06/04/2021
 Descrizione...: Programma per la visualizzazione e gestione dei table space di Oracle
"""

# Librerie sistema
import sys
# Librerie di data base
import cx_Oracle
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError

class table_space_class(FlaskForm):
	"""
	   classe per creazione campi all'interno dell'html
	"""	
	e_server_name = SelectField('Oracle name server:')	
	b_carica_table_space = SubmitField("Load")
       
def get_elenco_table_space(o_preferenze, e_server_name):
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
    v_select = """SELECT DF.TABLESPACE_NAME "TABLESPACE",
                            ROUND(TU.TOTALUSEDSPACE * 100 / DF.TOTALSPACE) "PERC_USED",
                            DF.TOTALSPACE "TOTAL MB",
                            TOTALUSEDSPACE "USED MB",
                            (DF.TOTALSPACE - TU.TOTALUSEDSPACE) "FREE MB"
                    FROM   (SELECT TABLESPACE_NAME,
                                    ROUND(SUM(BYTES) / 1048576) TOTALSPACE
                            FROM   DBA_DATA_FILES
                            GROUP BY TABLESPACE_NAME) DF,
                            (SELECT ROUND(SUM(BYTES)/(1024*1024)) TOTALUSEDSPACE,
                                    TABLESPACE_NAME
                            FROM   DBA_SEGMENTS
                            GROUP BY TABLESPACE_NAME) TU
                    WHERE DF.TABLESPACE_NAME = TU.TABLESPACE_NAME
                    AND DF.TOTALSPACE <> 0
                    ORDER BY ROUND(TU.TOTALUSEDSPACE * 100 / DF.TOTALSPACE) DESC
                """        
            
    # carico i dati
    v_cursor.execute(v_select)        
    
    # intestazioni     
    v_html = '<table class="table table-hover sortable">'
    v_html += """<thead> <tr> 
                        <th>Tablespace name</th> 
                        <th style="text-align:right">% Used</th> 
                        <th style="text-align:right">Total MByte</th> 
                        <th style="text-align:right">Used MByte</th> 
                        <th style="text-align:right">Free MByte</th> 
                        <th style="text-align:center">Details</th> 
                </tr> </thead>"""

    # carico la matrice dei dati 
    v_html += '<tbody id="id_my_table">'
    for row in v_cursor:                    
        v_html += '<tr>'
        
        v_html += '<td>' + str(row[0]) + '</td>'
        v_html += '<td style="text-align:right">' + str(row[1]) + '</td>'
        v_html += '<td style="text-align:right">' + str(row[2]) + '</td>'
        v_html += '<td style="text-align:right">' + str(row[3]) + '</td>'
        v_html += '<td style="text-align:right">' + str(row[4]) + '</td>'

        # nel pulsante dei dettagli annego i seguenti riferimenti: server, nome table space
        v_html += '<td align="center">  <a href="table_space_details?p_server='+e_server_name+'&p_table_space_name='+str(row[0])+'"> <i class="fas fa-info"> </i> </a> </td>'            
        
        v_html += '</tr>'
            
    # chiudo tabella html
    v_html += '</tbody> </table>'
            
    # chiudo sessione
    v_cursor.close()
    v_connection.close()
    
    # restituisco tabella
    return v_html                                                                                     