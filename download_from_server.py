# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6
 Data..........: 22/03/2021
 Descrizione...: Programma che scarica dal server iAS12g Oracle un sorgente form-report 
"""

#Librerie sistema
import sys
import os
import subprocess
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError

class download_from_server_class(FlaskForm):
	"""
	   classe per creazione campi all'interno dell'html
	"""	
	e_source = TextField('Source object name:',  [validators.required()])
	b_esegue = SubmitField('Get file from server')	
       
def execute_download_from_server(p_pwd, e_source):
    """
        Esegue download oggetto da iAS12g
        nella cartella temp\download_from_ias
    """                                      
    #imposto i nomi dei file su cui ridirigere output dei comandi (in questo modo non escono le brutte window di dos)    
    v_sshoutput = open(os.path.join(os.path.normpath('temp\\'), 'sshoutput.txt'), 'w')
    v_sshoutputerror = open(os.path.join(os.path.normpath('temp\\'), 'sshoutputerror.txt'), 'w')
    v_sshinput = ''    
    
    # eseguo il download
    # scarico il file nella directory indicata            
    v_ip = '10.0.4.14'        
    v_destinazione = os.path.join(os.path.dirname(os.path.realpath(__file__)) + '\\temp\\download_from_ias\\' + e_source)  
    v_command = 'echo y | utility_prog\\pscp -pw ' + p_pwd + ' oracle@' + v_ip + ':/appl/source/' + e_source + ' ' + v_destinazione
    print(v_command)
    v_ssh = subprocess.Popen(v_command, shell=True, stdin=subprocess.PIPE, stdout=v_sshoutput, stderr=v_sshoutputerror)
    v_ssh.communicate(v_sshinput)
    
    # controllo se il file è stato effettivamente scaricato       
    if os.path.isfile(v_destinazione):                
        return v_destinazione       
    else:
        return 'Error to download!'      