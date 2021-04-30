# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 02/04/2021
 Descrizione...: Programma per interrogare la storia di un job Oracle
"""

#Librerie di data base
import cx_Oracle
    
def job_history(o_preferenze, p_server, p_job_name):
    """
       Restituisce tabella html con history del job
       In input l'oggetto delle preferenze, il nome del server e il nome del job
    """            
    try:
        # connessione al DB come amministratore
        v_connection = cx_Oracle.connect(user=o_preferenze.v_oracle_user_sys,
                                        password=o_preferenze.v_oracle_password_sys,
                                        dsn=p_server,
                                        mode=cx_Oracle.SYSDBA)            
    except:
        return 'Connection to oracle rejected!'        

    # apro cursori
    v_cursor = v_connection.cursor()
        
    # select per la ricerca degli oggetti invalidi
    v_select = """SELECT TO_CHAR(REQ_START_DATE,'DD/MM/YYYY HH24:MI:SS') REQ_START_DATE,
                            TO_CHAR(EXTRACT(HOUR FROM RUN_DURATION), 'FM00') || ':' || TO_CHAR(EXTRACT(MINUTE FROM RUN_DURATION), 'FM00') || ':' || TO_CHAR(EXTRACT(SECOND FROM RUN_DURATION), 'FM00') RUN_DURATION, 
                            LOG_DATE,
                            STATUS,
                            ERRORS
                    FROM   ALL_SCHEDULER_JOB_RUN_DETAILS 
                    WHERE  JOB_NAME='""" + p_job_name + """' 
                    ORDER BY LOG_DATE DESC"""        
            
    v_cursor.execute(v_select)        
    
    # intestazioni (la classe sortable funziona solo se nella pagina html si è inserito lo specifico plugin)        
    v_html = '<table class="table w-auto sortable">'          
    v_html += """<thead> <tr> <th>Start date</th> 
                              <th>Run duration</th> 
                              <th>End date</th> 
                              <th>Status</th> 
                              <th>Additional info</th>                               
                  </tr> </thead>
              """                            
    # carico la matrice dei dati
    v_html += '<tbody id="id_my_table">'    
    for row in v_cursor:                    
        # apertura riga
        v_html += '<tr>'
                
        # nella cella del nome job includo anche le icone di gestione (la stringa &ensp; serve per inserire degli spazi)
        v_html += '<td>' + str(row[0]) + '</td>'    
        v_html += '<td>' + str(row[1]) + '</td>'    
        v_html += '<td>' + str(row[2]) + '</td>'    
        
        if str(row[3]) == 'FAILED':
            v_html += '<td style="background-color:red;color:white;">'+ str(row[3]) + '</td>'    
        else:
            v_html += '<td>' + str(row[3]) + '</td>'    
        
        v_html += '<td>' + str(row[4]) + '</td>'                    

        # chiusura riga
        v_html += '</tr>'
            
    # chiudo tabella html
    v_html += '</tbody> </table>'          
                    
    # chiudo sessione
    v_cursor.close()
    v_connection.close()
    
    # restituisco tabella html
    return v_html                             