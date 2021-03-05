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
from flask import Flask, render_template, request, flash, url_for, redirect
from preferenze import preferenze
from recompiler import recompiler_class

# Crea l'applicazione Flask
app = Flask(__name__)
# Stacco una secret key che serve alla funzione flash
app.config['SECRET_KEY'] = '013579'

# carico le preferenze
o_preferenze = preferenze()    
o_preferenze.carica()

# Apertura della pagina principale (quanto il cliente richiederà accesso al sito web verrà chiamata questa funzione che restituisce la pagina home.html
@app.route('/')
def home():    
    v_nome_utente = 'Hi!'
    return render_template('home.html', nome_utente=v_nome_utente)	
	
# Apertura della pagina ricerca stringa
@app.route('/search_string')
def search_string():        
    return render_template('search_string.html')		
	
# Apertura della pagina di recompiler
@app.route('/recompiler', methods=('GET', 'POST'))
def recompiler():
	# importa librerie necessarie
	from recompiler import ricerca_oggetti_invalidi
	from recompiler import compila_tutto
	
	form = recompiler_class()
	
	# controllo cosa ha richiesto l'utente premendo su uno dei pulsanti
	v_tab_html = ''
	if request.method == 'POST':
		e_server_name = form.e_server_name.data		
		# è stato richiesto di visualizzare gli oggetti invalidi
		if request.form.get('b_oggetti_invalidi'):
			v_tab_html = ricerca_oggetti_invalidi(o_preferenze, e_server_name)			
		# è stato richiesto di compilare gli oggetti invalidi
		elif request.form.get('b_compila_tutto'):
			# ricompilo
			v_ok = compila_tutto(o_preferenze, e_server_name)
			# se tutto ok --> emetto messaggio e rigenero la lista degli oggetti invalidi
			if v_ok == 'ok':
				flash('Invalid objects recompiled!')				
				v_tab_html = ricerca_oggetti_invalidi(o_preferenze, e_server_name)
	
	# restituisco la pagina
	return render_template('recompiler.html', 
							python_form=form, 
							python_elenco_righe=v_tab_html)	
	
# Apertura della pagina rubrica
@app.route('/books')
def books(): 	
	# importa librerie necessarie
	from rubrica import load_rubrica
    
	# alla funzione load_rubrica gli passo il tipo di rubrica T=Telefonica e eventuale parametro di ricerca
	return render_template('books.html', python_elenco_righe=load_rubrica())		
		
# Apertura della pagina di info
@app.route('/info', methods=('GET', 'POST'))
def info():
	# importa librerie necessarie
	import json
	from datetime import datetime
	
	if request.method == 'POST':
		# attivo il messaggio in alto alla pagina (v. info.html)
		flash("Thanks for the question. I'll get back to you soon :-)")
		
		# scrivo nel file un elemento json contenente le informazioni inseriti dell'utente
		v_json = {}
		v_json['questions'] = []
		v_json['questions'].append({
		'data': str(datetime.now()),
		'nome': request.form['inputNome'],
		'email' : request.form['inputEmail'],
		'messaggio' : request.form['textMessaggio']
		})
		# accodamento nel file questions.txt dell'oggetto json
		with open('questions.txt', 'a') as outfile:json.dump(v_json, outfile)
			
	return render_template('info.html')