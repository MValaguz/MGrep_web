# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 15/03/2021
 Descrizione...: Programma che visualizza elenco delle sessioni aperte in ambiente oracle. Restituisce una div html da inserire in una pagina web.
"""

# Librerie sistema
import sys
# Librerie di data base
import cx_Oracle
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError

class sessions_list_class(FlaskForm):
	"""
	   classe per creazione campi all'interno dell'html
	"""	
	e_server_name = SelectField('Oracle name server:')    
	b_load_list = SubmitField("Load list")	
       
def get_elenco_sessioni(o_preferenze, e_server_name):
    """
        restituisce un tabella html con elenco delle sessioni
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
    
    # select per la ricerca
    v_select = "SELECT SID,       \n\
                        SERIAL#,   \n\
                        TERMINAL,  \n\
                        USERNAME,  \n\
                        DECODE((SELECT DESCRIZIONE('MS_UTN','NOME_DE','LOGIN_CO',NULL,NULL,TERMINAL,NULL,'I','I') FROM DUAL),NULL,(SELECT DESCRIZIONE('MS_UTN','NOME_DE','LOGIN_CO',NULL,NULL,USERNAME,NULL,'I','I') FROM DUAL),(SELECT DESCRIZIONE('MS_UTN','NOME_DE','LOGIN_CO',NULL,NULL,TERMINAL,NULL,'I','I') FROM DUAL)) COGNOME_NOME, \n\
                        STATUS STATO, \n\
                        MODULE PROGRAMMA, \n\
                        PROG_DE DESCRIZIONE, \n\
                        ACTION AZIONE, \n\
                        LOGON_TIME \n\
                FROM   V$SESSION,(SELECT PROG_CO, PROG_DE FROM ML_PROG WHERE LNG_CO = 'I') ML_PROG \n\
                WHERE  USERNAME NOT IN ('SYS','SYSTEM','DBSNMP') AND MODULE = PROG_CO(+) \n\
                ORDER BY ROWNUM"
    
    v_cursor.execute(v_select)        
    
    # carico i risultati in una matrice
    matrice_dati = v_cursor.fetchall()
                
    # chiudo sessione
    v_cursor.close()
    v_connection.close()
    
    # intestazioni (la classe sortable funziona solo se nella pagina html si è inserito lo specifico plugin)
    v_html = '<table class="table table-hover sortable">'      
    v_html += '<thead> <tr> <th>Sid</th> <th>Serial Nr.</th> <th>Terminal</th> <th>Session Name</th> <th>User Name</th> <th>Status</th> <th>Program</th> <th>Description</th> <th>Action</th> <th>Logon time</th> <th style="text-align:center">Kill session</th> <th style="text-align:center">Info</th> </tr> </thead>'    
                            
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
        v_html += '<td>' + str(row[7]) + '</td>'    
        v_html += '<td>' + str(row[8]) + '</td>'            
        v_html += '<td>' + str(row[9]) + '</td>'            

        # nel pulsante di kill session annego il rif alla pagina che killa le sessioni con i seguenti parametri: server, sid e numero di serie
        v_html += '<td align="center">  <a href="session_kill?p_server='+e_server_name+'&p_sid='+str(row[0])+'&p_serial='+str(row[1])+'&p_page=sessions_list"> <i class="fas fa-power-off"> </i> </a> </td>'            
        # nel pulsante di info session annego il rif alla pagina che crea un file da scaricare contenente tutte le info della sessione aperta
        v_html += '<td align="center">  <a href="session_info?p_server='+e_server_name+'&p_sid='+str(row[0])+'&p_page=sessions_list"> <i class="fas fa-info"> </i> </a> </td>'            
        
        # chiusura riga
        v_html += '</tr>'
            
    # chiudo tabella html
    v_html += '</tbody> </table>'
    
    return v_html                                    

def get_totale_sessioni_per_utente(o_preferenze, e_server_name):
    """
        restituisce il numero totale utenti collegati 
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

    # select per il conteggio delle sessioni aperte per utente. Se il modulo è ICOM viene preso il campo terminale
    v_select = "SELECT COUNT(*) \n\
                FROM (SELECT DECODE(MODULE,'UNIFACE.EXE',TERMINAL,USERNAME) \n\
                        FROM   V$SESSION,(SELECT PROG_CO, PROG_DE FROM ML_PROG WHERE LNG_CO = 'I') ML_PROG \n\
                        WHERE  USERNAME NOT IN ('SYS','SYSTEM','DBSNMP') AND MODULE = PROG_CO(+) \n\
                               GROUP BY DECODE(MODULE,'UNIFACE.EXE',TERMINAL,USERNAME) \n\
                        )" 
                                
    # lettura dei dati e restituzione del campo totale
    v_cursor.execute(v_select)        
    matrice_dati = v_cursor.fetchone()

    return str(matrice_dati[0])
            
# ----------------------------------------
# TEST APPLICAZIONE
# ----------------------------------------
if __name__ == "__main__":    
    #Librerie interne MGrep
    from preferenze import preferenze
    
    # carico le preferenze
    o_preferenze = preferenze()    
    o_preferenze.carica()    
        
    print(get_elenco_sessioni(o_preferenze, 'BACKUP_815'))
    print(get_totale_sessioni_per_utente(o_preferenze, 'BACKUP_815'))