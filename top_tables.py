# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 08/04/2021
 Descrizione...: Programma per la ricerca delle tabelle che occupano più spazio nel database Oracle
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

class top_tables_class(FlaskForm):
    """
        classe per creazione campi all'interno dell'html
    """	
    e_server_name = SelectField('Oracle name server:')    
    b_ricerca = SubmitField("Start top tables search")	    
       
def ricerca_top_tables(o_preferenze, e_server_name):
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
    # select per la ricerca degli oggetti invalidi
    v_select = '''SELECT table_name, 
                            sum(bytes)/1024/1024 MB
                    FROM   (SELECT segment_name table_name, owner, bytes
                            FROM   dba_segments
                            WHERE  segment_type = 'TABLE'
                            
                            UNION  ALL
                            
                            SELECT i.table_name, i.owner, s.bytes
                            FROM   dba_indexes i, 
                                    dba_segments s
                            WHERE  s.segment_name = i.index_name
                            AND  s.owner = i.owner
                            AND  s.segment_type = 'INDEX'
                            
                            UNION ALL
                        
                            SELECT l.table_name, l.owner, s.bytes
                            FROM   dba_lobs l, 
                                    dba_segments s
                            WHERE  s.segment_name = l.segment_name
                            AND  s.owner = l.owner
                            AND  s.segment_type = 'LOBSEGMENT'
                            
                            UNION ALL
                    
                            SELECT l.table_name, l.owner, s.bytes
                            FROM   dba_lobs l, 
                                    dba_segments s
                            WHERE  s.segment_name = l.index_name
                            AND  s.owner = l.owner
                            AND  s.segment_type = 'LOBINDEX')
                            
                    WHERE owner = UPPER('SMILE')
                    AND table_name NOT LIKE '%$%'                
                    GROUP BY table_name, owner
                    ORDER BY SUM(bytes) desc 
                '''

    # carico tutte le righe in una lista
    v_cursor.execute(v_select)       
    matrice_dati = v_cursor.fetchall()                    
    
    # chiudo sessione
    v_cursor.close()
    v_connection.close()

    # intestazioni     
    v_html = '<table class="table table-hover sortable">'
    v_html += '<thead> <tr> <th>Table name</th> <th style="text-align:right">MByte</th> </tr> </thead>'
                            
    # carico la matrice dei dati
    v_html += '<tbody id="id_my_table">'
    v_index = 0
    v_totale = 0
    v_top_ten_labels = ''
    v_top_ten_data = ''
    for row in matrice_dati:                    
        # apertura riga
        v_html += '<tr>'
        
        v_html += '<td>' + str(row[0]) + '</td>'    
        v_html += '<td style="text-align:right">' + str(row[1]) + '</td>'    
        
        # chiusura riga
        v_html += '</tr>'

        # calcolo totale
        v_totale += row[1]

        # popolo la lista dei nomi delle 10 maggiori tabelle (es. "MA_PRAGE", "MA_MAMOV")
        # popolo la lista dei dati delle 10 maggiori tabelle (es. 100,50 ecc)
        v_index += 1
        if v_index <= 10:
            if v_index > 1:
                v_top_ten_labels += ','
                v_top_ten_data += ','
            v_top_ten_labels += '"' + row[0] + ' MByte"'
            v_top_ten_data += str(row[1])
            
    # chiudo tabella html
    v_html += '</tbody> </table>'

    # imposto la stringa del totale di spazio occulto
    v_text_totale = ''
    if v_totale > 0:            
        v_text_totale = 'Totale space '
        v_text_totale += ' MByte= ' + str(locale.format_string('%.2f', v_totale, grouping=True)) 
        v_text_totale += ', GByte= ' + str(locale.format_string('%.2f', v_totale/1000, grouping=True)) 
        v_text_totale += ', TByte= ' + str(locale.format_string('%.2f', v_totale/1000/1000, grouping=True)) 
    
    # restituisco la tabella html e il suo totale
    return v_html, v_text_totale, v_top_ten_labels, v_top_ten_data