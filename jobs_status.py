# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 31/03/2021
 Descrizione...: Programma per interrogare i job di sistema Oracle
"""

#Librerie sistema
import sys
import os
#Librerie di data base
import cx_Oracle
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField, BooleanField
from wtforms import validators, ValidationError

class jobs_status_class(FlaskForm):
    """
       classe per creazione campi all'interno dell'html
    """
    e_server_name = SelectField('Oracle name server:')    
    c_enable = BooleanField('Only jobs disabled:')
   
    b_ricerca_jobs = SubmitField('Start')
                                                                
def get_elenco_jobs(o_preferenze, e_server_name, c_enable):
    """
        Restituisce in una tupla elenco dei jobs di sistema
    """
    try:
        # connessione al DB come amministratore
        v_connection = cx_Oracle.connect(user=o_preferenze.v_oracle_user_sys,
                                         password=o_preferenze.v_oracle_password_sys,
                                         dsn=e_server_name,
                                         mode=cx_Oracle.SYSDBA)            
    except:
        return 'Connection to oracle rejected.'        

    # apro cursori
    v_cursor = v_connection.cursor()
    
    # job abilitati-disabilitati
    v_where = ''
    if c_enable:
        v_where = "ENABLED='FALSE'"
    else:
        v_where = "ENABLED='TRUE'"        
    
    # eventuale stringa di ricerca per nome o commento del job        
    #if self.e_search1.displayText() != '':
    #    v_where += " AND (JOB_NAME LIKE '%" + self.e_search1.displayText() + "%' OR COMMENTS LIKE '%" + self.e_search1.displayText() + "')" 
                            
    # select per la ricerca degli oggetti invalidi
    v_select = """SELECT JOB_NAME, 
                         COMMENTS,                                
                         JOB_ACTION, 
                         STATE,
                         TO_CHAR(LAST_START_DATE,'DD/MM/YYYY HH24:MI:SS') LAST_START_DATE,
                         TO_CHAR(LAST_START_DATE+LAST_RUN_DURATION,'DD/MM/YYYY HH24:MI:SS') LAST_END_DATE,                                                      
                         to_char(extract(HOUR FROM LAST_RUN_DURATION), 'fm00') || ':' || to_char(extract(MINUTE FROM LAST_RUN_DURATION), 'fm00') || ':' || to_char(extract(SECOND FROM LAST_RUN_DURATION), 'fm00') LAST_RUN_DURATION,      
                         (SELECT STATUS
                          FROM   ALL_SCHEDULER_JOB_RUN_DETAILS 
                          WHERE  ALL_SCHEDULER_JOB_RUN_DETAILS.JOB_NAME=ALL_SCHEDULER_JOBS.JOB_NAME
                            AND ALL_SCHEDULER_JOB_RUN_DETAILS.LOG_DATE=(SELECT Max(LOG_DATE)
                                                                        FROM   ALL_SCHEDULER_JOB_RUN_DETAILS
                                                                         WHERE  ALL_SCHEDULER_JOB_RUN_DETAILS.JOB_NAME=ALL_SCHEDULER_JOBS.JOB_NAME)
                         ) LAST_STATUS,
                         (SELECT ADDITIONAL_INFO
                          FROM   ALL_SCHEDULER_JOB_RUN_DETAILS
                          WHERE  ALL_SCHEDULER_JOB_RUN_DETAILS.JOB_NAME=ALL_SCHEDULER_JOBS.JOB_NAME
                             AND ALL_SCHEDULER_JOB_RUN_DETAILS.LOG_DATE=(SELECT Max(LOG_DATE)
                                                                         FROM   ALL_SCHEDULER_JOB_RUN_DETAILS
                                                                         WHERE  ALL_SCHEDULER_JOB_RUN_DETAILS.JOB_NAME=ALL_SCHEDULER_JOBS.JOB_NAME)
                         ) ADDITIONAL_INFO,
                         TO_CHAR(NEXT_RUN_DATE,'DD/MM/YYYY HH24:MI:SS') NEXT_RUN_DATE
                    FROM   ALL_SCHEDULER_JOBS 
                    WHERE  """ + v_where.upper() + """
                    ORDER BY JOB_NAME"""        
            
    v_cursor.execute(v_select)  

    # intestazioni (la classe sortable funziona solo se nella pagina html si è inserito lo specifico plugin)        
    v_html = '<table class="table w-auto small sortable">'      
    v_html += """<thead> <tr> <th>Job name</th> 
                              <th>Comments</th> 
                              <th>Job action</th> 
                              <th>State</th> 
                              <th>Last start date</th> 
                              <th>Last end date</th> 
                              <th>Last run duration</th> 
                              <th>Last status</th> 
                              <th>Additional info</th> 
                              <th>Next run date</th> 
                  </tr> </thead>
              """
                            
    # carico la matrice dei dati
    v_html += '<tbody id="id_my_table">'    
    for row in v_cursor:                    
        # apertura riga
        v_html += '<tr>'
                
        # nella cella del nome job includo anche le icone di gestione (la stringa &ensp; serve per inserire degli spazi)
        v_html += '<td>' + str(row[0]) + '<br>'
        v_html += '<a href="job_history?p_server='+e_server_name+'&p_job_name='+str(row[0])+'&p_page=jobs_status" title="List of past executions status"> <i class="fas fa-history"> </i>&ensp;</a>'
        v_html += '<a href="job_action?p_action=stop&p_server='+e_server_name+'&p_job_name='+str(row[0])+'&p_page=jobs_status" title="Stop the execution job (only if job is in running status)"> <i class="fas fa-stop"> </i>&ensp;</a>'
        v_html += '<a href="job_action?p_action=start&p_server='+e_server_name+'&p_job_name='+str(row[0])+'&p_page=jobs_status" title="Start the job immediatly"> <i class="fas fa-play"> </i>&ensp;</a>'
        v_html += '<a href="job_action?p_action=disable&p_server='+e_server_name+'&p_job_name='+str(row[0])+'&p_page=jobs_status" title="Disable the execution of the job forever"> <i class="fas fa-pause"> </i>&ensp;</a>'
        v_html += '<a href="job_action?p_action=enable&p_server='+e_server_name+'&p_job_name='+str(row[0])+'&p_page=jobs_status" title="Enable the execution of the job"> <i class="fas fa-forward"> </i>&ensp;</a> '
        v_html += '</td>'    

        v_html += '<td>' + str(row[1]) + '</td>'    
        v_html += '<td>' + str(row[2]) + '</td>'    
        
        if str(row[3]) == 'RUNNING':
            v_html += '<td style="background-color:green;color:white;">'+ str(row[3]) + '</td>'    
        else:
            v_html += '<td>' + str(row[3]) + '</td>'            

        v_html += '<td>' + str(row[4]) + '</td>'    
        v_html += '<td>' + str(row[5]) + '</td>'    
        v_html += '<td>' + str(row[6]) + '</td>'    
        
        if str(row[7]) == 'FAILED':
            v_html += '<td style="background-color:red;color:white;">'+ str(row[7]) + '</td>'    
        else:
            v_html += '<td>' + str(row[7]) + '</td>'    
        
        v_html += '<td>' + str(row[8]) + '</td>'            
        v_html += '<td>' + str(row[9]) + '</td>'            

        # chiusura riga
        v_html += '</tr>'
            
    # chiudo tabella html
    v_html += '</tbody> </table>'          
                    
    # chiudo sessione
    v_cursor.close()
    v_connection.close()
    
    # restituisco tabella html
    return v_html                        