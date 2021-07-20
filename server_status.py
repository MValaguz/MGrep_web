# -*- coding: UTF-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6
 Data..........: 07/04/2021
 Descrizione...: Set di utility per consultare situazione di un server linux dove installato DB Oracle                 
"""

#Libreria sistema
import  os
import  subprocess
               
def action_disc_usage(o_preferenze):
    """
        Restituisce 6 stringhe con la situazione dischi dei server
    """
    # spazio disco icom_815
    v_text1 = spazio_disco("10.0.4.10", o_preferenze.v_server_password_DB)        
    
    # spazio disco backup_815
    v_text2 = spazio_disco("10.0.4.11", o_preferenze.v_server_password_DB) 
    
    # spazio disco backup_2_815
    v_text3 = spazio_disco("10.0.4.12", o_preferenze.v_server_password_DB)
    
    # spazio disco ias_smile_reale
    v_text4 = spazio_disco("10.0.4.14", o_preferenze.v_server_password_iAS)  
    
    # spazio disco ias_smile_backup
    v_text5 = spazio_disco("10.0.47.47", o_preferenze.v_server_password_iAS)
    
    # spazio disco ias_smile_backup2
    v_text6 = spazio_disco("10.0.47.45", o_preferenze.v_server_password_iAS)

    return v_text1, v_text2, v_text3,  v_text4, v_text5, v_text6
        
def spazio_disco(p_ip_server, p_pwd):        
    """
        Funzione che esegue il comando "df -h" sul server indicato e lo restituisce come stringa di output
        Attenzione! Utente di collegamento è oracle
    """
    # imposto i nomi dei file su cui ridirigere output dei comandi (in questo modo non escono le brutte window di dos)
    v_sshoutput = open(os.path.join('temp', 'sshoutput.txt'), 'w')
    v_sshoutputerror = open(os.path.join('temp', 'sshoutputerror.txt'), 'w')
    v_sshinput = ''
            
    try:
        #spazio del disco. Il comando vero e proprio è "df -h"
        v_command = 'echo y | utility_prog\\plink -pw ' + p_pwd + ' oracle@' + p_ip_server + ' df -h '            
        v_ssh = subprocess.Popen(v_command, shell=True, stdin=subprocess.PIPE, stdout=v_sshoutput, stderr=v_sshoutputerror)
        v_ssh.communicate(v_sshinput)
    except:
        return 'Plink command error on ' + p_ip_server + '!'        
    
    # leggo il risultato e lo visualizzo 
    return open(os.path.join('temp', 'sshoutput.txt'), 'r').read()    

def action_top_sessions(o_preferenze):
    """               
        Carica nelle varie sezioni il risultato del comando top sessions
    """
    # spazio disco icom_815
    v_text1 = top("10.0.4.10",o_preferenze.v_server_password_DB)
    
    # spazio disco backup_815
    v_text2 = top("10.0.4.11",o_preferenze.v_server_password_DB)
    
    # spazio disco backup_2_815
    v_text3 = top("10.0.4.12",o_preferenze.v_server_password_DB)
    
    # spazio disco ias_smile_reale
    v_text4 = top("10.0.4.14",o_preferenze.v_server_password_iAS)
    
    # spazio disco ias_smile_backup
    v_text5 = top("10.0.47.47",o_preferenze.v_server_password_iAS)
    
    # spazio disco ias_smile_backup2
    v_text6 = top("10.0.47.45",o_preferenze.v_server_password_iAS)
    
    return v_text1, v_text2, v_text3,  v_text4, v_text5, v_text6
    
def top(p_ip_server, p_pwd):        
    """
        Funzione che esegue il comando "top" sul server indicato e lo restituisce come stringa di output
        Nello specifico l'opzione -b indica di mandare l'output sul file e -n il numero di iterazioni da svolgere 
        Attenzione! Utente di collegamento è oracle
    """
    #imposto i nomi dei file su cui ridirigere output dei comandi (in questo modo non escono le brutte window di dos)
    v_sshoutput = open(os.path.join('temp', 'sshoutput.txt'), 'w')
    v_sshoutputerror = open(os.path.join('temp', 'sshoutputerror.txt'), 'w')
    v_sshinput = ''
            
    try:
        #comando top con opzione -b (esecuzione in batch) e iterazioni 1
        v_command = 'echo y | utility_prog\\plink -pw ' + p_pwd + ' oracle@' + p_ip_server + ' top -b -n 1 '            
        v_ssh = subprocess.Popen(v_command, shell=True, stdin=subprocess.PIPE, stdout=v_sshoutput, stderr=v_sshoutputerror)
        v_ssh.communicate(v_sshinput)
    except:
        return 'Plink command error on ' + p_ip_server + '!'
    
    # leggo il risultato e lo visualizzo 
    return open(os.path.join('temp', 'sshoutput.txt'), 'r').read()   

def action_show_folder_ora02(o_preferenze):
    """
        Mostra il contenuto della cartella ora02 dove sono presenti i file di journaling che crea Oracle
        In realtà esiste anche la cartella gemella ora03
        Viene eseguito solo per i server dove montato Oracle DB
    """
    # spazio disco icom_815
    v_text1 = folder_ora02("10.0.4.10",o_preferenze.v_server_password_DB)
    
    # spazio disco backup_815
    v_text2 = folder_ora02("10.0.4.11",o_preferenze.v_server_password_DB)
    
    # spazio disco backup_2_815
    v_text3 = folder_ora02("10.0.4.12",o_preferenze.v_server_password_DB)
    
    # spazio disco ias_smile_reale
    v_text4 = ''
    
    # spazio disco ias_smile_backup
    v_text5 = ''
    
    # spazio disco ias_smile_backup2
    v_text6 = ''
    
    return v_text1, v_text2, v_text3,  v_text4, v_text5, v_text6
    
def folder_ora02(p_ip_server, p_pwd):        
    """
        Funzione che esegue il comando "ls" sul server indicato e lo restituisce come stringa di output           
        Attenzione! Utente di collegamento è oracle
    """
    #imposto i nomi dei file su cui ridirigere output dei comandi (in questo modo non escono le brutte window di dos)
    v_sshoutput = open(os.path.join('temp', 'sshoutput.txt'), 'w')
    v_sshoutputerror = open(os.path.join('temp', 'sshoutputerror.txt'), 'w')
    v_sshinput = ''
            
    try:
        #comando list con opzione verticale (-l) e unità di misura megabyte (-h)
        v_command = 'echo y | utility_prog\\plink -pw ' + p_pwd + ' oracle@' + p_ip_server + ' ls -lh /ora02/arch/'            
        v_ssh = subprocess.Popen(v_command, shell=True, stdin=subprocess.PIPE, stdout=v_sshoutput, stderr=v_sshoutputerror)
        v_ssh.communicate(v_sshinput)
    except:
        return 'Plink command error on ' + p_ip_server + '!'        
    
    # leggo il risultato e lo visualizzo 
    return open(os.path.join('temp', 'sshoutput.txt'), 'r').read()                 