# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 12/03/2021
 Descrizione...: Programma per la ricerca di blocchi di sessione inerenti una tabella in ambiente oracle. Restituisce una div html da inserire in una pagina web.
"""

# Librerie sistema
import sys
# Librerie di data base
import cx_Oracle
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, SelectField

class table_locks_class(FlaskForm):
    """
        classe per creazione campi all'interno dell'html
    """	
    e_server_name = SelectField('Oracle name server:')
    e_table_name = TextField('Table name:')        
    b_ricerca_blocchi = SubmitField("Check sessions locks")	    
       
def ricerca_blocchi_tabella(o_preferenze, e_server_name, e_table_name):
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

    # select per la ricerca degli oggetti invalidi
    v_select = """SELECT    v$lock.SID  SID, 
                            v$session.SERIAL# SERIAL_NUMBER, 
                            V$SESSION.USERNAME USERNAME,
                            V$SESSION.STATUS STATUS, 
                            V$SESSION.OSUSER OSUSER, 
                            V$SESSION.MACHINE MACHINE,
                            V$SESSION.PROGRAM||'.'||V$SESSION.MODULE PROGRAM
                FROM v$lock, v$session
                WHERE id1 = (SELECT object_id
                                FROM   all_objects
                                WHERE  owner ='SMILE' AND
                                    object_name = RTRIM(LTRIM(UPPER('""" + e_table_name + """')))) AND 
                        v$lock.sid=v$session.sid"""
    v_cursor.execute(v_select)        
    
    # carico tutte le righe in una lista
    matrice_dati = v_cursor.fetchall()                    
    
    # chiudo sessione
    v_cursor.close()
    v_connection.close()

    # intestazioni     
    v_html = '<table class="table table-hover sortable">'
    v_html += '<thead> <tr> <th>Sid</th> <th>Serial Nr.</th> <th>Username</th> <th>Status</th> <th>Os User</th> <th>Machine</th> <th>Program</th> <th style="text-align:center">Kill session</th> </tr> </thead>'    
                            
    # carico la matrice dei dati
    v_html += '<tbody id="id_my_table">'
    for row in matrice_dati:                    
        # apertura riga
        v_html += '<tr>'
        
        v_html += '<td>' + str(row[0]) + '</td>'    
        v_html += '<td>' + str(row[1]) + '</td>'    
        v_html += '<td>' + str(row[2]) + '</td>'    
        v_html += '<td>' + str(row[3]) + '</td>'    
        v_html += '<td>' + str(row[4]) + '</td>'    
        v_html += '<td>' + str(row[5]) + '</td>'    
        v_html += '<td>' + str(row[6]) + '</td>'    

        # nel pulsante di kill session annego il rif alla pagina che killa le sessioni con i seguenti parametri: server, sid e numero di serie
        v_html += '<td align="center">  <a href="session_kill?p_server='+e_server_name+'&p_sid='+str(row[0])+'&p_serial='+str(row[1])+'&p_page=table_locks"> <i class="fas fa-power-off"> </i> </a> </td>'            
        
        # chiusura riga
        v_html += '</tr>'
            
    # chiudo tabella html
    v_html += '</tbody> </table>'
    
    return v_html                                    
        
# ----------------------------------------
# TEST APPLICAZIONE
# ----------------------------------------
if __name__ == "__main__":    
    #Librerie interne MGrep
    from preferenze import preferenze
    
    # carico le preferenze
    o_preferenze = preferenze()    
    o_preferenze.carica()    
        
    print(ricerca_blocchi_tabella(o_preferenze, 'BACKUP_815', 'MA_ANART'))