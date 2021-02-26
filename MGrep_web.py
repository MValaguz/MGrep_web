# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 con libreria Flask
 Data..........: 03/02/2021
 Descrizione...: Questa è la versione web di MGrep!
"""

# Pacchetti da installare
# pip install Flask
# pip install cx_oracle==5.3 

# Per avviare...: Avviare la virtualenv c:\PythonFlask\Scripts\activate
#                 Spostarsi nella dir c:\Users\MValaguz\Documents\Flask_Progetto2\
#                 Settare per Windows (set FLASK_APP=Flask_Progetto2.py) che indica a flask il programma python root
#                 
#                 Avviare Flask in modalità sviluppo 
#                   - Settare per Windows il debug (set FLASK_ENV=development) che permette il riavvio automatico ogni volta che viene modificato un sorgente
#                   - Avviare il server con (python -m flask run) 
#
#                 Avviare Flask in modalità server 
#                   - Avviare con (python -m flask run --host=0.0.0.0); in questo caso si potrà accedere al sito con http://10.0.47.9:5000/ (dove 10.0.47.9 è l'indirizzo ip del PC su cui gira flask)
#
from flask import Flask
from flask import Flask, render_template
from rubrica import load_rubrica

# Crea l'applicazione Flask
app = Flask(__name__)

# Impostazione della path
#app.static_folder = app.root_path + "\\templates"

# Visualizzazione delle path di ambiente. Nella templates si trovano i sorgenti html mentre nella static tutti gli oggetti richiamati dalle pagine html
#print('--------------------')
#print('Root path --> ' + app.root_path)
#print('Static folder --> ' + app.static_folder)
#print('--------------------')

# Apertura della pagina principale (quanto il cliente richiederà accesso al sito web verrà chiamata questa funzione che restituisce la pagina home.html
@app.route('/')
def home():    
    v_nome_utente = 'Hi!'
    return render_template('home.html', nome_utente=v_nome_utente)	
	
# Apertura della pagina ricerca stringa
@app.route('/search_string')
def search_string():        
    return render_template('search_string.html')		
	
# Apertura della pagina rubrica
@app.route('/books')
def books(): 	
    # alla funzione load_rubrica gli passo il tipo di rubrica T=Telefonica e eventuale parametro di ricerca
	return render_template('books.html', python_elenco_righe=load_rubrica())		
	
# Apertura della pagina di help
@app.route('/info')
def info():        
    return render_template('info.html')		