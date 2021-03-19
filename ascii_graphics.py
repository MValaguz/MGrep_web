# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Data..........: 19/03/2021
 Descrizione...: Dato un testo, lo converte in big text

 Nota..........: Fa affidamento alla libreria pyfiglet
"""

#Librerie sistema
import sys
import os
#Librerie per convertire caratteri ascii in big text
import pyfiglet 
# Importa librerie per creazione form
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError
# Librerie utilità
from utilita import file_in_directory

def carica_lista_fonts():
    """
        Restituisce lista con elenco dei fonts (in pratica i files contenuti nella directory fonts di python)        
    """         
    v_pyfiglet_fonts_dir = pyfiglet.__file__
    v_pyfiglet_fonts_dir = os.path.dirname(v_pyfiglet_fonts_dir)
    v_root_node = v_pyfiglet_fonts_dir + '\\fonts'        
    v_elenco_file = file_in_directory(v_root_node)
    v_lista_finale = []
    # inserisco un primo elemento vuoto
    v_lista_finale.append('')
    #v_lista_finale.append(v_root_node) questa è una riga utile per eventuale debug in quanto inserisce come primo elemento il nome della cartella dove va a cercare i font
    for nome_file in v_elenco_file:
        # filtro l'elenco dei file prendendo solo quelli con il suffisso .flf che sono quelli dei font disponibili
        if nome_file.find('.flf')>0:                
            # estrae solo il nome del file dalla stringa
            v_solo_nome_file = os.path.basename(nome_file)                
            # nella lista aggiunge solo la parte del nome senza il suffisso                
            v_lista_finale.append(os.path.splitext(v_solo_nome_file)[0])
    return v_lista_finale    

class ascii_graphics_class(FlaskForm):
    """
        classe per creazione campi all'interno dell'html
    """	
    e_fonts_list = SelectField('Ascii graphics fonts available:', choices=carica_lista_fonts() )
    e_converte = TextField('Insert a text to convert:', [validators.required()])        
    b_esegue = SubmitField("Convert")	    
   
def converte_in_big_text(e_fonts_list, e_converte):
    """
        Dato un testo e_converte, lo converte in big text usando il font e_fonts_list
    """                
    # il risultato viene impostato con il font richiesto (da non confondersi con il font con cui viene visualizzato)    
    if e_fonts_list != '':
        risultato = pyfiglet.figlet_format( e_converte, font=e_fonts_list )         
    # se però non è stato indicato alcun fonts, lascio il default
    else:
        risultato = pyfiglet.figlet_format( e_converte )         
    # restituisco il risultato
    return risultato