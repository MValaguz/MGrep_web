# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 12/03/2021
 Descrizione...: Programma per la ricerca di blocchi di sessione in ambiente oracle. Restituisce una div html da inserire in una pagina web.
"""

# Librerie sistema
import sys
# Librerie di data base
import cx_Oracle
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError

class sessions_locks_class(FlaskForm):
	"""
	   classe per creazione campi all'interno dell'html
	"""	
	e_server_name = SelectField('Oracle name server:')
	b_ricerca_blocchi = SubmitField("Check sessions locks")	
       
def ricerca_blocchi_sessioni(o_preferenze, e_server_name):
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

    # select per la ricerca degli oggetti bloccati
    v_select = "WITH sessions AS \n\
                (SELECT sid, serial#, blocking_session, P2, row_wait_obj#, sql_id, username,terminal,program \n\
                    FROM v$session) \n\
                    SELECT sid,  serial#, username, terminal, program, object_name, level \n\
                    FROM (SELECT sid, serial#, blocking_session, P2, row_wait_obj#, sql_id, username,terminal,program \n\
                        FROM v$session) s \n\
                    LEFT OUTER JOIN dba_objects \n\
                    ON (object_id = row_wait_obj#) \n\
                    WHERE sid IN (SELECT blocking_session FROM sessions) \n\
                    OR blocking_session IS NOT NULL \n\
                CONNECT BY PRIOR sid = blocking_session \n\
                START WITH blocking_session IS NULL"
    
    v_cursor.execute(v_select)        
    
    # integro i risultati della prima select con altri dati e li carico in una tupla
    matrice_dati = []
    for result in v_cursor:
        # ricerco il posizionamento del PC in termini di locazione e referente
        v_location = ''
        v_referent = ''
        v_phone    = ''
        v_ricerca_sql = v_connection.cursor()
        # campo di ricerca (nome pc o nome utente)
        if str(result[3]) == '':
            v_utente = str(result[2])
        else:
            v_utente = str(result[3])

        v_ricerca_sql.execute("""SELECT HW_DISPO.NOME_DE, 
                                        HW_DISPO.DISLO_DE,  
                                        CP_DIPEN.DIPEN_DE,  
                                        VA_RUBRICA.TELIN_NU   
                                FROM   SMILE.HW_DISPO,     
                                        SMILE.MA_CESPH,     
                                        SMILE.CP_DIPEN,     
                                        SMILE.VA_RUBRICA    
                                WHERE  UPPER(HW_DISPO.NOME_DE) LIKE '%""" + v_utente + """%'  AND 
                                        MA_CESPH.AZIEN_CO = HW_DISPO.AZIEN_CO AND 
                                        MA_CESPH.MATRI_CO = HW_DISPO.MATRI_CO AND  
                                        MA_CESPH.UTAZI_CO = CP_DIPEN.AZIEN_CO AND  
                                        MA_CESPH.UTMAT_CO = CP_DIPEN.DIPEN_CO AND  
                                        VA_RUBRICA.AZIEN_CO = CP_DIPEN.AZIEN_CO AND 
                                        VA_RUBRICA.DIPEN_CO = CP_DIPEN.DIPEN_CO""")
        
        for campi in v_ricerca_sql:
            if v_location == '':
                v_location = campi[1]
            if v_referent == '':
                v_referent = campi[2]
            if v_phone == '':
                v_phone    = campi[3]
        
        # carico la riga nella tupla (notare le doppie parentesi iniziali che servono per inserire nella tupla una lista :-))
        matrice_dati.append( ( str(result[0]), str(result[1]), str(result[2]), str(result[3]), str(v_referent), str(v_phone), str(v_location), str(result[4]), str(result[5]), result[6] ) )            
                
    # chiudo sessione
    v_cursor.close()
    v_connection.close()

    # intestazioni     
    v_html = '<table class="table table-hover sortable">'
    v_html += '<thead> <tr> <th>Sid</th> <th>Serial Nr.</th> <th>Username</th> <th>Terminal</th> <th>Referent</th> <th>Phone</th> <th>Location</th> <th>Program</th> <th>Object Name</th> <th style="text-align:center">Kill session</th> </tr> </thead>'    
                            
    # carico la matrice dei dati. Nel campo sid inserisco degli spazi in base al valore del campo level 
    v_html += '<tbody id="id_my_table">'
    for row in matrice_dati:                    
        # apertura riga
        v_html += '<tr>'
        
        # dettagli (nella colonna 9 di matrice_dati è presente il campo level della prima select)
        # viene inoltre creata una colonna che permette di avere un ref alla pagina di chiusura di una sessione
        v_spazi = ''
        if row[9] > 1:
            v_spazi = '&ensp;' * row[9]

        v_html += '<td>' + v_spazi + str(row[0]) + '</td>'    
        v_html += '<td>' + str(row[1]) + '</td>'    
        v_html += '<td>' + str(row[2]) + '</td>'    
        v_html += '<td>' + str(row[3]) + '</td>'    
        v_html += '<td>' + str(row[4]) + '</td>'    
        v_html += '<td>' + str(row[5]) + '</td>'    
        v_html += '<td>' + str(row[6]) + '</td>'    
        v_html += '<td>' + str(row[7]) + '</td>'    
        v_html += '<td>' + str(row[8]) + '</td>'            

        # nel pulsante di kill session annego il rif alla pagina che killa le sessioni con i seguenti parametri: server, sid e numero di serie
        v_html += '<td align="center">  <a href="session_kill?p_server='+e_server_name+'&p_sid='+str(row[0])+'&p_serial='+str(row[1])+'&p_page=sessions_locks"> <i class="fas fa-power-off"> </i> </a> </td>'            
        
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
        
    print(ricerca_blocchi_sessioni(o_preferenze, 'BACKUP_815'))