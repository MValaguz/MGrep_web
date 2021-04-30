# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6
 Data..........: 11/12/2019
 Descrizione...: Classe per la gestione delle preferenze del programma MGrep 
"""

import os
import platform
import base64

def cripta_testo(testo):
    """
       Cripta una stringa con la chiave mgrep. Il valore restituito è di tipo byte
    """
    key = 'mgrep_2020'
    enc = []
    for i in range(len(testo)):
        key_c = key[i % len(key)]
        enc_c = (ord(testo[i]) + ord(key_c)) % 256
        enc.append(enc_c)
    return base64.urlsafe_b64encode(bytes(enc))    

def decripta_testo(btesto):
    """
       decripta una serie di byte con la chiave mgrep. Il valore restituito è di tipo stringa
    """
    key = 'mgrep_2020'
    dec = []
    enc = base64.urlsafe_b64decode(btesto)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + enc[i] - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

class preferenze:
    def __init__(self):
        """
            Definizione delle proprietà della classe preferenze
        """
        self.v_oracle_user_sys = 'SYS'
        
        # caricamento delle password da file criptati...se non trovate uscirà messaggio di avviso all'avvio di MGrep
        try:
            v_file = open('pwd\\mgrep_pwd_sys.pwd','r')
            v_pwd = decripta_testo( v_file.read() )
            self.v_oracle_password_sys = v_pwd
        except:
            self.v_oracle_password_sys = ''
        try:
            v_file = open('pwd\\mgrep_pwd_oracle_dba.pwd','r')
            v_pwd = decripta_testo( v_file.read() )
            self.v_server_password_DB = v_pwd
        except:
            self.v_server_password_DB = ''
        try:
            v_file = open('pwd\\mgrep_pwd_ias.pwd','r')
            v_pwd = decripta_testo( v_file.read() )        
            self.v_server_password_iAS = v_pwd
        except:
            self.v_server_password_iAS = ''

        # imposto default campi ricerca stringa
        self.pathname = 'W:/source'
        self.excludepath = '00-Standards e Guidelines,01-Moduli e Tabelle,02-Documentazione OLD,03-Template,04-FAQ,05-Manutenzioni e Trasferimenti DB,06-Aggiornamento_giornaliero,99-Prove,MO-SMILE Mobile'        
        self.filter = '.fmb,.rdf'
        self.flsearch = True
        self.dboracle1 = 'SMILE/SMILE@BACKUP_815'
        self.dboracle2 = 'SMI/SMI@BACKUP_815'
        self.dbsearch = True
        self.icomsearch = True

        # imposto default campi import-export                
        self.sqlite_db = os.path.normpath('MGrepTransfer.db')
        
		# preferenze elenco server
        self.elenco_server = ['ICOM_815','BACKUP_815','BACKUP_2_815']

# ------------------------
# test della classe
# ------------------------
if __name__ == "__main__":
    ###
    # Parte1 = Inizializzazione oggetto e stampa dei suoi default
    ###
    o_preferenze = preferenze()
    print('-'*100)
    print('Valori preferenze di default')
    print('-'*100)
    for index in o_preferenze.__dict__:
        print(index + ((40-len(index))*' ') + ' => ' + str(o_preferenze.__dict__[index]))
