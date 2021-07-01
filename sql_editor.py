# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6
 Data..........: 22/06/2021
 Descrizione...: Scopo dello script è gestire un editor di sql 
"""
# Librerie di data base
import cx_Oracle
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField
# Libreria utilità di database
from utilita_database import nomi_colonne_istruzione_sql

class sql_editor_class(FlaskForm):
    """
        Classe per creazione campi all'interno dell'html
    """	
    e_server_name = SelectField('Oracle name server:')
    e_schema = SelectField('Oracle schema:', choices = ['SMILE','SMI'])	    
    e_sql = TextAreaField('SQL statement')	    
    b_sql_execute = SubmitField('Execute sql')

def sql_execute(e_server_name, e_schema, e_sql):
    """
        Esegue statement sql
    """    
    try:
        # connessione al DB come amministratore
        v_connection = cx_Oracle.connect(user=e_schema,
                                         password=e_schema,
                                         dsn=e_server_name)            
    except:
        return 'Connection to oracle rejected!'            

    # apro cursore
    v_cursor = v_connection.cursor()

    # all'sql scritto dall'utente aggiungo una parte che mi permette di avere la colonna id riga
    # questa colonna mi servirà per tutte le operazioni di aggiornamento
    e_sql = 'SELECT ROWID, MY_SQL.* FROM (' + e_sql + ') MY_SQL'    
    try:
        v_cursor.execute(e_sql)        
    except cx_Oracle.Error as e:                                
        errorObj, = e.args                        
        return "Error: " + errorObj.message

    # ricavo i nomi delle colonne della query per creare le intestazioni della tabella
    # la prima colonna, siccome contiene id della riga, viene sempre nascosta
    v_html = '<thead> <tr>'          
    intestazioni = nomi_colonne_istruzione_sql(v_cursor)                            
    x = 0
    for nome_campo in intestazioni:
        if x == 0:
            v_html += '<th style="display:none">'
        else:
            v_html += '<th class="text-center">' 
        
        v_html += nome_campo + '</th>'
        x += 1

    # chiudo intestazione
    v_html += '</thead> </tr>'          
        
    # carico le righe della tabella        
    v_html += '<tbody>'          
    while True:
        row = v_cursor.fetchone()
        if row == None:
            break
        else:            
            # apro la riga
            v_html += '<tr>'
            x = 0
            # carico il contenuto della riga         
            for field in row:                                                
                # la prima colonna è sempre l'id della riga che viene nascosto
                if x == 0:
                    v_html += '<td style="display:none">'
                else:
                    v_html += '<td class="row_data pt-3-half" contenteditable="true">'
                
                # in base al tipo di campo eseguo le dovute conversioni                
                # campo nullo
                if field == None:    
                    v_html += '</td>'       
                # se il contenuto è un clob...utilizzo il metodo read sul campo field, poi lo inserisco in una immagine                
                elif v_cursor.description[x][1] == cx_Oracle.BLOB:                                                                            
                    v_html += '<img src="static/img/file.jpg"></td>'       
                    #qimg = QtGui.QImage.fromData(field.read())                        
                else:
                    v_html += str(field) + '</td>'   
                # incremento contatore colonna
                x += 1                     
        
            # chiudo la riga
            v_html += '</tr>'
            
    # chiudo tabella html
    v_html += '</tbody>'
            
    # chiudo sessione
    v_cursor.close()
    v_connection.close()    

    return v_html                                    