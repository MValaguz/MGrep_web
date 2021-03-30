# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 24/03/2021
 Descrizione...: Programma per visualizzare il carico del DB Oracle in termini di CPU ecc.
                 Contrariamente a quanto si possa immaginare, ottenere queste informazioni non è facile.
                 Le metriche che Oracle rende disponibili tramite la vista v$sesstat sono comulative, nel senso
                 che fanno riferimento al momento in cui vengono lette rispetto alla data-ora di accensione del sistema.
                 Se ad esempio leggo la metrica relativa all'occupazione della CPU (da non intendersi come CPU fisica ma
                 del motore di DB) della sessione MVALAGUZ in questo momento ottengo 10 come valore. Questo valore 
                 indica l'occupazione da parte della sessione da quando si è collegata.
                 Quindi il programma è stato impostato in questo modo:
                 - Vengono utilizzate 2 pagine di UT_REPORT (nel DB locale SQLITE) dove:
                   1a pagina - Alla prima esecuzione contiene la situazione di partenza (inizio monitoraggio)
                   2a pagina - Contiene la situazione al momento del campionamento successivo
                 - Dopo aver effettuato il campionamento nella pagina2, essa viene confrontata con la pagina1 e 
                   la pagina1 viene aggiornata con i nuovi valori (sessioni sparite, sessioni nuove, valori nuovi).
                   Sempre sulla pagina1 viene poi eseguito il calcolo della percentuale di valore
                 Attenzione! Non vengono estratte tutte le sessioni perché ci sono processi oracle che non interessano.
"""

#Librerie sistema
import sys
import os
import datetime
#Librerie di data base
import cx_Oracle
#Librerie interne MGrep
from utilita_database import t_report_class
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField

class form_top_sessions_class(FlaskForm):
    """
        classe per creazione campi all'interno dell'html
    """	
    e_server_name = SelectField('Oracle name server:')
    e_parameter = SelectField('Parameter:')        
    b_compute = SubmitField("Create start point")	    

def elenco_parametri():
    """
       restituisce lista con elenco parametri di controllo
    """
    return ['CPU used by this session',
            'physical reads',
            'db block gets',
            'recursive calls',
            'consistent gets',
            'redo size',
            'bytes sent via SQL*Net to client',
            'bytes received via SQL*Net from client',
            'SQL*Net roundtrips to/from client',
            'sorts (memory)',
            'sorts (disk)']        

class oracle_top_sessions_class():
    """
        Oracle session
        In input: tutto l'oggetto preferenze, il nome del server scelto a video e il parametro scelto a video
    """       
    def __init__(self, p_preferenze, e_server_name, e_parameter):
        # carico internamente le preferenze
        self.o_preferenze = p_preferenze        

        # nome del server e parametro scelto
        self.e_server_name = e_server_name
        self.e_parameter = e_parameter
                
        # apro t_report (tre pagine) nel db che viene creato-salvato in temp 
        self.fname = 'TOP_SESSIONS'
        self.t_report = t_report_class( os.path.normpath('temp\\top_sessions.db') )
        self.page1 = self.t_report.new_page(self.fname)
        self.page2 = self.t_report.new_page(self.fname)
        
        # chiudo il db (questo perché in ambito web i thread cambiano e sqlite va in errore)
        self.t_report.close(p_commit=True)
                                                
    def starter(self):
        """
           Caricamento della pagina iniziale
        """
        # apro db sqlite
        self.t_report = t_report_class( os.path.normpath('temp\\top_sessions.db') )

        # connessione al DB come amministratore
        try:
            self.oracle_con = cx_Oracle.connect(user=self.o_preferenze.v_oracle_user_sys,
                                                password=self.o_preferenze.v_oracle_password_sys,
                                                dsn=self.e_server_name,
                                                mode=cx_Oracle.SYSDBA)            
        except:
            return 'Connection to oracle rejected.'            
        
        # cancello il contenuto delle pagine di ut_report (tranne record posizione 0)
        self.t_report.delete_page(self.fname, self.page1)
        
        # carico in pagina1 di ut_report, il punto di partenza della situazione sessioni         
        self.load_from_oracle_top_sessions(self.page1)
                                                                        
    def load_from_oracle_top_sessions(self, p_page):
        """
            Carica nella pagina di ut_report indicata da p_page la query delle sessioni Oracle
        """
        # pulisco la pagina
        self.t_report.delete_page(self.fname, p_page)
        
        # apro cursore oracle
        v_cursor = self.oracle_con.cursor()
        
        # select per la ricerca degli oggetti invalidi        
        v_select = """select se.sid,
                             username,
                             status,
                             logon_time,
                             round ((sysdate-logon_time)*1440*60) logon_secs,                                                          
                             nvl(se.module, se.program) module_info,
                             se.sql_id,
                             (select min(sql_text) from V$SQL WHERE sql_id=se.sql_id) sql_text,
                             value
                      from   v$session se,
                             v$sesstat ss,
                             v$statname sn
                      where  username is not null
                        and  se.sid=ss.sid
                        and  sn.statistic#=ss.statistic#
                        and  sn.name in ('""" + self.e_parameter + """')
                   """        
                
        v_cursor.execute(v_select)        
        
        # salvo in t_report 
        v_row = []
        for result in v_cursor:
            self.t_report.insert(p_commit=False,
                                 p_fname_co=self.fname, 
                                 p_page_nu=p_page, 
                                 p_campo1=result[0], 
                                 p_campo2=result[1],
                                 p_campo3=result[2], 
                                 p_campo4=result[3], 
                                 p_campo26=result[4],                                   
                                 p_campo6=result[5], 
                                 p_campo7=result[6], 
                                 p_campo8=result[7],
                                 p_campo21=result[8]) 
                  
        # chiudo cursore oracle
        self.t_report.commit()
        v_cursor.close()
        
    def load_screen(self, p_page):            
        """
            Carica a video la pagina di ut_report indicata
        """
        # apro db sqlite
        self.t_report = t_report_class( os.path.normpath('temp\\top_sessions.db') )

        # carico in una tupla i dati
        self.t_report.execute("""SELECT IFNULL(CAMPO24,''),
                                        IFNULL(CAMPO1,''),
                                        IFNULL(CAMPO2,''),
                                        IFNULL(CAMPO3,''),
                                        IFNULL(CAMPO4,''),
                                        IFNULL(CAMPO22,''),
                                        IFNULL(CAMPO21,''),
                                        IFNULL(CAMPO23,''), 
                                        IFNULL(CAMPO26,''),
                                        IFNULL(CAMPO6,''),
                                        IFNULL(CAMPO7,''),
                                        IFNULL(CAMPO8,'')
                                FROM   UT_REPORT
                                WHERE  FNAME_CO = ?
                                  AND  PAGE_NU = ?
                                  AND  POSIZ_NU > 0
                                ORDER BY CAMPO24 DESC, CAMPO3""", 
                            (self.fname, p_page))
        
        matrice_dati = self.t_report.curs.fetchall()

        # intestazioni 
        v_html = '<table class="table w-auto small sortable">'      
        v_html += '<thead> <tr> <th>%</th> <th>Sid</th> <th>User name</th> <th>Status</th> <th>Logon</th> <th>Value Now</th> <th>Value Old</th> <th>Variance</th> <th>Logon Time</th> <th>Module</th> <th>SQL Id</th> <th>SQL Text</th> </tr> </thead>'
                                
        # carico la matrice dei dati
        v_html += '<tbody id="id_my_table">'
        v_total_rows = 0
        for row in matrice_dati:                    
            # apertura riga
            v_html += '<tr>'
            v_total_rows += 1
            
            v_html += '<td style="text-align:right">' + str(row[0]) + '</td>'    
            v_html += '<td style="text-align:right">' + str(row[1]) + '</td>'    
            v_html += '<td>' + str(row[2]) + '</td>'    
            v_html += '<td>' + str(row[3]) + '</td>'    
            v_html += '<td>' + str(row[4]) + '</td>'    
            v_html += '<td style="text-align:right">' + str(row[5]) + '</td>'    
            v_html += '<td style="text-align:right">' + str(row[6]) + '</td>'    
            v_html += '<td style="text-align:right">' + str(row[7]) + '</td>'    
            v_html += '<td style="text-align:right">' + str(row[8]) + '</td>'    
            v_html += '<td>' + str(row[9]) + '</td>'    
            v_html += '<td>' + str(row[10]) + '</td>'    
            v_html += '<td>' + str(row[11]) + '</td>'    

            # chiusura riga
            v_html += '</tr>'

        # aggiungo riga totale
        v_html += '<tr> <td> </td> <td> </td> <td> TOTAL SESSIONS:' + str(v_total_rows) + '</td> </tr>'
                
        # chiudo tabella html
        v_html += '</tbody> </table>'

        # restituisco tabella
        return v_html
    
    def calc_differenze(self):
        """
           Questo è di fatto il cuore del programma!
           Calcolo differenze tra pagina2 e pagina1 e il risultato lo metto nella pagina1
           
           Schema utilizzo dei campi di UT_REPORT 
           CAMPO1 = SID
           CAMPO2  = USERNAME
           CAMPO3  = STATUS
           CAMPO4  = LOGON_TIME (data e ora di logon della sessione)
           CAMPO26 = LOGON_SECS (tempo di connessione in secondi)           
           CAMPO6  = MODULE_INFO
           CAMPO7  = SQL_ID
           CAMPO8  = SQL_TEXT
           CAMPO21 = VALORE OLD DELLA METRICA (es. cpu)
           CAMPO22 = VALORE NOW DELLA METRICA (es. cpu)
           CAMPO23 = DIFFERENZA TRA VALORE OLD E VALORE NOW
           CAMPO24 = PERCENTUALE 
        """
        # apro db sqlite
        self.t_report = t_report_class( os.path.normpath('temp\\top_sessions.db') )

        # carico la nuova situazione delle sessioni dentro la pagina2
        self.load_from_oracle_top_sessions(self.page2)
        
        #--
        # Attenzione! Essendoci un solo cursore aperto e dovendo fare una lettura di più tabelle incrociate, si caricano
        # i dati in matrici
        #-- 
        
        #--
        # STEP1 - elimino dalla pagina1 tutte quelle sessioni che NON sono presenti nella2. Vuol dire che nel frattempo 
        #         sono state chiuse
        #--
        self.t_report.execute("""SELECT * 
                                 FROM  UT_REPORT 
                                 WHERE FNAME_CO = ?
                                   AND PAGE_NU  = ? 
                                   AND POSIZ_NU > 0""", (self.fname, self.page1))
        # leggo tutta la pagina1
        tabella = self.t_report.curs.fetchall()
        for riga_pag1 in tabella:
            # decodifico la riga in modo sia un dizionario "parlante"
            v_rec_pag1 = self.t_report.decode(riga_pag1)
            # controllo se la sessione è ancora presente nella nuova situazione
            self.t_report.execute("""SELECT COUNT(*)
                                     FROM   UT_REPORT
                                     WHERE  FNAME_CO = ?
                                       AND  PAGE_NU  = ?
                                       AND  CAMPO1   = ?
                                       AND  CAMPO2   = ?""", (self.fname, self.page2, v_rec_pag1['CAMPO1'], v_rec_pag1['CAMPO2']) )
            v_count = self.t_report.curs.fetchone()[0]
            
            #print(v_rec_pag1['CAMPO1'] + ' utente ' + v_rec_pag1['CAMPO2'] + ' ' + str(v_count))
            # se la sessione non è presente --> la cancello dalla pagina1
            if v_count == 0:
                print('Sessione eliminata ' + str(v_rec_pag1['CAMPO1']) + ' utente ' + v_rec_pag1['CAMPO2'])
                self.t_report.execute("""DELETE 
                                         FROM   UT_REPORT
                                         WHERE  FNAME_CO = ?
                                           AND  PAGE_NU  = ?
                                           AND  CAMPO1   = ?
                                           AND  CAMPO2   = ?""", (self.fname, self.page1, v_rec_pag1['CAMPO1'], v_rec_pag1['CAMPO2']) )                
            
        #--
        # STEP2 - Partendo dalla pagina2, carico nella pagina1 tutte le nuove sessioni, 
        #--        
        self.t_report.execute("""SELECT * 
                                 FROM  UT_REPORT 
                                 WHERE FNAME_CO = ?
                                   AND PAGE_NU  = ? 
                                   AND POSIZ_NU> 0""", (self.fname, self.page2))
        tabella = self.t_report.curs.fetchall()    
        for riga_pag2 in tabella:
            # decodifico la riga in modo sia un dizionario "parlante"
            v_rec_pag2 = self.t_report.decode(riga_pag2)
            # ricerco se presente nella pagina1 (elaborazione precedente) la stessa sessione con lo stesso username 
            self.t_report.execute("""SELECT * 
                                     FROM   UT_REPORT 
                                     WHERE  FNAME_CO = ?
                                       AND  PAGE_NU= ? 
                                       AND  CAMPO1 = ? 
                                       AND  CAMPO2 = ?""", (self.fname, self.page1, v_rec_pag2['CAMPO1'], v_rec_pag2['CAMPO2']) )
            riga_pag1 = self.t_report.curs.fetchone()
            if riga_pag1 != None:
                # decodifico la riga in modo sia un dizionario "parlante"
                v_rec_pag1 = self.t_report.decode(riga_pag1)                
                # aggiorno la colonna22 della pagina1 che contiene il NUOVO valore. Inoltre aggiorno anche SQL_ID e SQL_Text 
                # in quanto potrebbero essere cambiati
                self.t_report.execute("""UPDATE UT_REPORT 
                                         SET    CAMPO22 = ?,
                                                CAMPO7 = ?,
                                                CAMPO8 = ?
                                         WHERE  FNAME_CO = ?
                                           AND  PAGE_NU = ? 
                                           AND  POSIZ_NU= ?""", 
                                        (v_rec_pag2['CAMPO21'], 
                                         v_rec_pag2['CAMPO7'], 
                                         v_rec_pag2['CAMPO8'], 
                                         v_rec_pag1['FNAME_CO'], 
                                         v_rec_pag1['PAGE_NU'], 
                                         v_rec_pag1['POSIZ_NU']) )
            else:
                # sessione non trovata, vuol dire che è stata aperta nel frattempo
                print('Nuova sessione ' + str(v_rec_pag2['CAMPO1']) + ' utente ' + v_rec_pag2['CAMPO2'])
                self.t_report.insert(p_commit  = True,
                                     p_fname_co= self.fname, 
                                     p_page_nu = self.page1, 
                                     p_campo1  = v_rec_pag2['CAMPO1'], 
                                     p_campo2  = v_rec_pag2['CAMPO2'],
                                     p_campo3  = v_rec_pag2['CAMPO3'], 
                                     p_campo4  = v_rec_pag2['CAMPO4'], 
                                     p_campo26 = v_rec_pag2['CAMPO26'],                                 
                                     p_campo6  = v_rec_pag2['CAMPO6'], 
                                     p_campo7  = v_rec_pag2['CAMPO7'], 
                                     p_campo8  = v_rec_pag2['CAMPO8'],
                                     p_campo21 = v_rec_pag2['CAMPO21']) 
        #--
        # STEP3 - In pagina1 calcolo la differenza tra il nuovo e il vecchio valore
        #--        
        self.t_report.execute("""UPDATE UT_REPORT 
                                 SET    CAMPO23 = ROUND(CAMPO22 - CAMPO21,0) 
                                 WHERE  FNAME_CO = ? 
                                   AND  PAGE_NU = ?""", (self.fname, self.page1) )  
        
        # calcolo il totale
        self.t_report.execute("""SELECT SUM(CAMPO23)
                                 FROM   UT_REPORT
                                 WHERE  FNAME_CO = ?
                                   AND  PAGE_NU  = ?""", (self.fname, self.page1) )
        v_totale = self.t_report.curs.fetchone()[0]
        
        # calcolo le percentuali rispetto al totale 
        self.t_report.execute("""UPDATE UT_REPORT 
                                 SET    CAMPO24 = ROUND(CAMPO23 * 100 / ?,1) 
                                 WHERE  FNAME_CO = ? 
                                   AND  PAGE_NU = ?""", (v_totale, self.fname, self.page1) )

        # commit
        self.t_report.commit()

if __name__=='__main__':
    from preferenze import preferenze
    
    o_preferenze = preferenze()
    o_preferenze.carica()
    
    v_test = oracle_top_sessions_class(o_preferenze, 'ICOM_815', 'CPU used by this session')
    v_test.starter()
    print(v_test.load_screen(v_test.page1))