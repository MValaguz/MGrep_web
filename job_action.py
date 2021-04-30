# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 02/04/2021
 Descrizione...: Esegue azioni di start, stop, ecc. su un job Oracle
"""

#Librerie di data base
import cx_Oracle

def job_stop(o_preferenze, p_server, p_job_name):
    """
        Interrompe un job
    """        
    try:
        # connessione al DB come amministratore
        v_connection = cx_Oracle.connect(user=o_preferenze.v_oracle_user_sys,
                                        password=o_preferenze.v_oracle_password_sys,
                                        dsn=p_server,
                                        mode=cx_Oracle.SYSDBA)            
    except:
        return 'Connection to oracle rejected!'                    
        
    # apro cursore
    v_cursor = v_connection.cursor()
    # imposto l'istruzione
    v_istruzione = "BEGIN DBMS_SCHEDULER.STOP_JOB (job_name => 'SMILE."+p_job_name+"'); END;"                    
    # eseguo istruzione monitorando eventuali errori
    try:
        v_cursor.execute( v_istruzione )                            
    # se riscontrato errore --> emetto sia codice che messaggio
    except cx_Oracle.Error as e:                                        
        errorObj, = e.args                
        return("Error: " + errorObj.message)                 
            
    # chiudo
    v_cursor.close()
    v_connection.close()

    return 'ok'
                
def job_start(o_preferenze, p_server, p_job_name):
    """
        Avvia un job
    """
    try:
        # connessione al DB come amministratore
        v_connection = cx_Oracle.connect(user=o_preferenze.v_oracle_user_sys,
                                        password=o_preferenze.v_oracle_password_sys,
                                        dsn=p_server,
                                        mode=cx_Oracle.SYSDBA)            
    except:
        return 'Connection to oracle rejected!'                    
        
    # apro cursore
    v_cursor = v_connection.cursor()
    # imposto l'istruzione
    v_istruzione = "BEGIN DBMS_SCHEDULER.RUN_JOB (job_name => 'SMILE."+p_job_name+"'); END;"                    
    # eseguo istruzione monitorando eventuali errori
    try:
        v_cursor.execute( v_istruzione )                            
    # se riscontrato errore --> emetto sia codice che messaggio
    except cx_Oracle.Error as e:                                        
        errorObj, = e.args                
        return("Error: " + errorObj.message)                 
            
    # chiudo
    v_cursor.close()
    v_connection.close()

    return 'ok'
    
def job_disable(o_preferenze, p_server, p_job_name):
    """
        Disattiva un job
    """
    try:
        # connessione al DB come amministratore
        v_connection = cx_Oracle.connect(user=o_preferenze.v_oracle_user_sys,
                                        password=o_preferenze.v_oracle_password_sys,
                                        dsn=p_server,
                                        mode=cx_Oracle.SYSDBA)            
    except:
        return 'Connection to oracle rejected!'                    
        
    # apro cursore
    v_cursor = v_connection.cursor()
    # imposto l'istruzione
    v_istruzione = "BEGIN DBMS_SCHEDULER.DISABLE (name => 'SMILE."+p_job_name+"'); END;"                    
    # eseguo istruzione monitorando eventuali errori
    try:
        v_cursor.execute( v_istruzione )                            
    # se riscontrato errore --> emetto sia codice che messaggio
    except cx_Oracle.Error as e:                                        
        errorObj, = e.args                
        return("Error: " + errorObj.message)                 
            
    # chiudo
    v_cursor.close()
    v_connection.close()

    return 'ok'

def job_enable(o_preferenze, p_server, p_job_name):
    """
        Riattiva un job
    """    
    try:
        # connessione al DB come amministratore
        v_connection = cx_Oracle.connect(user=o_preferenze.v_oracle_user_sys,
                                        password=o_preferenze.v_oracle_password_sys,
                                        dsn=p_server,
                                        mode=cx_Oracle.SYSDBA)            
    except:
        return 'Connection to oracle rejected!'                    
        
    # apro cursore
    v_cursor = v_connection.cursor()
    # imposto l'istruzione
    v_istruzione = "BEGIN DBMS_SCHEDULER.ENABLE (name => 'SMILE."+p_job_name+"'); END;"                    
    # eseguo istruzione monitorando eventuali errori
    try:
        v_cursor.execute( v_istruzione )                            
    # se riscontrato errore --> emetto sia codice che messaggio
    except cx_Oracle.Error as e:                                        
        errorObj, = e.args                
        return("Error: " + errorObj.message)                 
            
    # chiudo
    v_cursor.close()
    v_connection.close()

    return 'ok'