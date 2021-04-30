# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6
 Data..........: 09/08/2018 
"""

import os
import sys
       
def file_in_directory(p_node):
    '''
       Restituisce tupla con elenco dei file contenuti nella dir p_node e nelle sue sottodir
    '''
    v_file = []
    for root, dirs, files in os.walk(p_node):
        # scorro le tuple dei nomi dentro tupla dei files
        for name in files:
            # stesso discorso istruzione precedente per quanto riguarda la directory (viene poi salvata nel file risultato)
            v_dir_name = os.path.join(root)
            # stesso discorso istruzione precedente per quanto riguarda il file (viene poi salvata nel file risultato)
            v_file_name = os.path.join(name)
            v_file.append(v_dir_name + '\\' + v_file_name)        
    # restituosco la tupla con l'elenco
    return v_file

def delete_files_in_dir(p_dir):
    """
       Elimina tutti i files della directory p_dir
    """
    for files in os.listdir(p_dir):        
        os.remove(files)

delete_files_in_dir('temp\\ta_files')        