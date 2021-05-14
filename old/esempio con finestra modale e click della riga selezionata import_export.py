"""
  queste funzioni vanno usate per caricare la tabella della modal page
  da notare come nella singola cella ci sia annegato il richiamo alla funzione Fn_pick..., funzione presente nella
  pagina html e che permette la selezione del valore di cella e la chiusura della modal
  
  Questo esperimento non è andato a buon fine in quanto flask non è proprio adatto alla gestione dinamica delle pagine web se non facendo
  particolari accrocchi
"""


def html_elenco_tabelle_sqlite(p_nome_sqlitedb):
    """
       Restituisce tabella html con elenco delle tabelle sqlite 
    """
    # intestazioni 
    v_html = '<table class="table table-hover">'      
    v_html += '<thead> <tr> <th>Table Name</th> </tr> </thead>'    
                            
    # carico la matrice dei dati
    v_html += '<tbody id="id_table_modal_pick_sqlite">'    
    for row in estrae_elenco_tabelle_sqlite('1', p_nome_sqlitedb):                    
        # apertura riga
        v_html += '<tr>'    
        # la funzione Fn_Leggi_Cella è nella parte html della pagina
        v_html += '<td onclick ="Fn_pick_sqlite(this)">' + str(row) + '</td>'        
        # chiusura riga
        v_html += '</tr>'
            
    # chiudo tabella html
    v_html += '</tbody> </table>'
    
    return v_html                

def html_elenco_tabelle_oracle(p_user, p_server):
    """
       Restituisce tabella html con elenco delle tabelle oracle
    """
    # intestazioni 
    v_html = '<table class="table table-hover">'      
    v_html += '<thead> <tr> <th>Table Name</th> </tr> </thead>'    
                            
    # carico la matrice dei dati
    v_html += '<tbody id="id_table_modal_pick_oracle">'    
    for row in estrae_elenco_tabelle_oracle( '1', p_user, p_user, p_server ):                    
        # apertura riga
        v_html += '<tr>'    
        # la funzione Fn_Leggi_Cella è nella parte html della pagina
        v_html += '<td onclick ="Fn_pick_oracle(this)">' + str(row) + '</td>'        
        # chiusura riga
        v_html += '</tr>'
            
    # chiudo tabella html
    v_html += '</tbody> </table>'
    
    return v_html                
