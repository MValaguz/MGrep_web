# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 con libreria pyqt5
 Data..........: 05/12/2019
 Descrizione...: Programma per la ricompilazione oggetti invalidi su DB oracle. Restituisce una div html da inserire in una pagina web.
"""

# Librerie sistema
import sys
# Librerie di data base
import cx_Oracle
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError

class recompiler_class(FlaskForm):
	"""
	   classe per creazione campi all'interno dell'html
	"""	
	e_server_name = SelectField('Oracle name server:')
	b_oggetti_invalidi = SubmitField("Search invalid objects")
	b_compila_tutto = SubmitField("Compile all invalid objects")
       
def ricerca_oggetti_invalidi(o_preferenze, e_server_name):
    """
        funzione che carica elenco degli oggetti invalidi
        restituendo una tabella html
    """    
    # connessione al DB come amministratore        
    try:
        v_connection = cx_Oracle.connect(user=o_preferenze.v_oracle_user_sys,
                                         password=o_preferenze.v_oracle_password_sys,
                                         dsn=e_server_name,
                                         mode=cx_Oracle.SYSDBA)                        
    except:
        # esco dalla funzione con l'errore di non connesso a oracle
        return 'Connection to oracle rejected!'        
        
    # apro cursori
    v_cursor = v_connection.cursor()
    # select per la ricerca degli oggetti invalidi
    v_cursor.execute("SELECT OWNER, OBJECT_NAME, OBJECT_TYPE  FROM ALL_OBJECTS WHERE STATUS='INVALID' AND OWNER NOT IN ('SYS','APEX_040200') AND OBJECT_NAME NOT LIKE 'OLAP_OLEDB%' ORDER BY OBJECT_TYPE")
    
    # carico tutte le righe in una lista
    matrice_dati = v_cursor.fetchall()            
    
    v_cursor.close()
    v_connection.close()                       
    
    # intestazioni     
    v_html = '<table class="table table-hover sortable">'
    v_html += '<thead> <tr> <th>Owner</th> <th>Object name</th> <th>Object type</th> </tr> </thead>'
                            
    # carico la matrice dei dati 
    v_html += '<tbody id="id_my_table">'
    for row in matrice_dati:                    
        v_html += '<tr>'
        for field in row:
            v_html += '<td>' + str(field) + '</td>'
        v_html += '</tr>'
            
    # chiudo tabella html
    v_html += '</tbody> </table>'
    
    return v_html
                                               
def compila_tutto(o_preferenze, e_server_name):
    """
        funzione che compila tutti gli oggetti invalidi
        restituendo una tabella html
    """
    try:
        # connessione al DB come amministratore
        v_connection = cx_Oracle.connect(user=o_preferenze.v_oracle_user_sys,
                                         password=o_preferenze.v_oracle_password_sys,
                                         dsn=e_server_name,
                                         mode=cx_Oracle.SYSDBA)
        v_error = False
    except:
        return 'Connection to oracle rejected!'        

    if not v_error:
        # apro cursori
        v_cursor = v_connection.cursor()

        # esecuzione dello script che ricompila tutti gli oggetti invalidi
        v_cursor.execute("BEGIN UTL_RECOMP.RECOMP_SERIAL(); END;")
        v_cursor.close()
        v_connection.close()

        # restituisco tutto ok
        return 'ok'
        
# ----------------------------------------
# TEST APPLICAZIONE
# ----------------------------------------
if __name__ == "__main__":    
    #Librerie interne MGrep
    from preferenze import preferenze
    
    # carico le preferenze
    o_preferenze = preferenze()    
    o_preferenze.carica()    
    
    print(compila_tutto(o_preferenze, 'ICOM_815'))
    print(ricerca_oggetti_invalidi(o_preferenze, 'ICOM_815'))