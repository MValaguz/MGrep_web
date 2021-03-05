# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 03/03/2021
 Descrizione...: Programma per la ricerca nella rubrica aziendale. Restituisce una div html da inserire in una pagina web.
"""

#Librerie sistema
import sys
#Librerie di data base
import cx_Oracle
       
def load_rubrica():
    """
        Restituisce una lista con elementi della rubrica        
    """                                                       
    try:
        # connessione al DB come amministratore
        v_connection = cx_Oracle.connect(user='SMILE', password='SMILE', dsn='ICOM_815')
    except:
        return 'Connection to oracle rejected!'

    # apro cursore
    v_cursor = v_connection.cursor()

    # definizione della select (per rubrica telefonica)    
    v_cursor.execute("SELECT AZIDP_DE, DIPEN_DE, CONTT_CO, REP_DE, EMAIL_DE, MANSIO_DE FROM VA_RUBRI WHERE CATEG_CO='T' AND AZIEN_CO IS NOT NULL AND DIPEN_DE IS NOT NULL ORDER BY AZIDP_DE")
    
    # carico tutte le righe in una lista
    matrice_dati = v_cursor.fetchall()

    # chiudo la connessione
    v_cursor.close()
    v_connection.close()
    
    # intestazioni 
    v_html = '<table class="table table-striped">'    
    v_html += '<thead> <tr> <th>Company</th> <th>Employee</th> <th>Phone</th> <th>Unit</th> <th>Email</th> <th>Function</th> </tr> </thead>'
                            
    # carico la matrice dei dati 
    v_html += '<tbody id="id_my_table_book">'
    for row in matrice_dati:                    
        v_html += '<tr>'
        for field in row:
            v_html += '<td>' + str(field) + '</td>'
        v_html += '</tr>'
            
    # chiudo tabella html
    v_html += '</tbody> </table>'
    
    return v_html
        
# ----------------------------------------
# TEST APPLICAZIONE
# ----------------------------------------
if __name__ == "__main__":    
    print( load_rubrica() )