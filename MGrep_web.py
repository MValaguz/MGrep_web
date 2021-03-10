# -*- coding: utf-8 -*-

"""
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 
 Librerie......: Flask = Gestione server
                 WTForms = Si occupa di gestire la sezione form di una pagina HTML permettendo 
				           uno scambio "semplificato" dei valori dei campi e dei controlli di
						   validità
				 cx_Oracle = Libreria per connessione a database Oracle
 Data..........: 03/02/2021
 Descrizione...: Questa è la versione web di MGrep!
"""

# Pacchetti da installare
# pip install Flask
# pip install cx_oracle==5.3 
# pip install WTForms==2.3.3

# Per avviare...: E' stato creato il file bat avvia_server.bat che contiene tutte le istruzioni per avviare il server Flask lato Windows e solo per sviluppo.
#                 Alcune note sui comandi presenti nel file avvia_server.bat
#                 SET FLASK_APP indica il nome del programma Python che gestisce il server
#                 SET FLASK_ENV indica la modalità dell'ambiente. Settando development si è in modalità di sviluppo, per cui ogni modifica agli oggetti 
#                 python -m flask run --host=0.0.0.0 in questo caso si potrà accedere al sito con http://10.0.47.9:5000/ (dove 10.0.47.9 è l'indirizzo ip del PC su cui gira flask)
#
from flask import Flask
from flask import Flask, render_template, request, flash, url_for, redirect
from preferenze import preferenze

# Crea l'applicazione Flask
app = Flask(__name__)
# Stacco una secret key che serve alla funzione flash
app.config['SECRET_KEY'] = '013579'

# carico le preferenze
o_preferenze = preferenze()    
o_preferenze.carica()

#---------------------------------------	
# Apertura della pagina principale 
#---------------------------------------	
@app.route('/')
def home():    
    v_nome_utente = 'Hi!'
    return render_template('home.html', nome_utente=v_nome_utente)	

#---------------------------------------	
# Apertura della pagina ricerca stringa
#---------------------------------------	
@app.route('/search_string')
def search_string():        
    return render_template('search_string.html')		
	
#---------------------------------------	
# Apertura della pagina di recompiler
#---------------------------------------	
@app.route('/recompiler', methods=('GET', 'POST'))
def recompiler():
	# importa librerie necessarie
	from recompiler import recompiler_class
	from recompiler import ricerca_oggetti_invalidi
	from recompiler import compila_tutto
	
	# creo la parte di form (elenco server e pulsanti), passando l'elenco dei server
	form = recompiler_class()
	# carico elenco dei server nel relativo campo
	form.e_server_name.choices = o_preferenze.elenco_server
	
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

#---------------------------------------	
# Apertura della pagina di sessions locks
#---------------------------------------	
@app.route('/sessions_locks', methods=('GET', 'POST'))
def sessions_locks():
	# importa librerie necessarie
	from sessions_locks import sessions_locks_class
	from sessions_locks import ricerca_blocchi_sessioni
	
	# creo la parte di form (elenco server e pulsanti), passando l'elenco dei server
	form = sessions_locks_class()
	# carico elenco dei server nel relativo campo
	form.e_server_name.choices = o_preferenze.elenco_server
	
	# controllo cosa ha richiesto l'utente premendo su uno dei pulsanti
	v_tab_html = ''
	if request.method == 'POST':
		e_server_name = form.e_server_name.data		
		# è stato richiesto di visualizzare gli oggetti invalidi
		if request.form.get('b_ricerca_blocchi'):
			v_tab_html = ricerca_blocchi_sessioni(o_preferenze, e_server_name)			
	
	# restituisco la pagina
	return render_template('sessions_locks.html', 
							python_form=form, 
							python_elenco_righe=v_tab_html)								

#---------------------------------------	
# Apertura della pagina di kill session
#---------------------------------------	
@app.route('/kill_session', methods=('GET', 'POST'))
def kill_session():
	# importa la funzione per killare la sessione
	from utilita_database import killa_sessione
	
	# visualizzo la finestra modale di richiesta chiusura sessione (il numero di sid viene passato come parametro nella pagina)
	v_server = request.args.get('p_server')	
	v_sid = request.args.get('p_sid')	
	v_serial_n = request.args.get('p_serial')	
	
	if request.method == 'POST':
		if request.form.get('b_cancel')=='click_b_cancel':
			return redirect(url_for('sessions_locks'))
		if request.form.get('b_kill')=='click_b_kill':
			# chiudo la sessione
			killa_sessione(
							v_sid, # colonna 0 della riga
							v_serial_n, # colonna 1 della riga
							o_preferenze.v_oracle_user_sys,
							o_preferenze.v_oracle_password_sys,
							v_server
						)    
			# ritorno alla pagina di partenza
			return redirect(url_for('sessions_locks'))
			
	# restituisco il rendering della pagina con numero di sid
	return render_template('kill_session.html', python_parametro_sid=v_sid)

#---------------------------------------	
# Apertura della pagina elenco telefonico
#---------------------------------------	
@app.route('/books')
def books(): 	
	# importa librerie necessarie
	from rubrica import load_rubrica
    
	# alla funzione load_rubrica gli passo il tipo di rubrica T=Telefonica e eventuale parametro di ricerca
	return render_template('books.html', python_elenco_righe=load_rubrica())		
		
#---------------------------------------	
# Apertura della pagina di info
# L'utente inserendo i dati nella sezione "question"
# invia la propria richiesta dentro il file di testo questions.txt
# le informazioni sono scritte nel formato json
#---------------------------------------	
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