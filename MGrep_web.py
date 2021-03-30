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
import datetime
from flask import Flask
from flask import Flask, render_template, request, flash, url_for, redirect, send_file
from preferenze import preferenze

# Crea l'applicazione Flask
app = Flask(__name__)
# Stacco una secret key che serve alla funzione flash
app.config['SECRET_KEY'] = '013579'

# carico le preferenze
o_preferenze = preferenze()    
o_preferenze.carica()

# variabile globale che contiene nomi di tabelle
# viene creata in quanto serve di supporto per le liste di valori
v_elenco_tabelle = ['']

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
@app.route('/search_string', methods=('GET', 'POST'))
def search_string():
	from search_string import search_string_class
	from search_string import carica_default
	from search_string import ricerca_stringhe

	# creo la parte di form 
	form = search_string_class()	
	
	# controllo se eseguire il post
	v_tab_html = ''		
	if request.method == 'POST':		
		if request.form.get('b_search'):
			v_errore, v_tab_html = ricerca_stringhe(form)					
		if v_errore != 'Ok':
			flash(v_errore)	
	# oppure caricare i default
	else:
		carica_default(form, o_preferenze)							
	
	return render_template('search_string.html',
							python_form=form,
							python_elenco_righe=v_tab_html)

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
	
	# carico la parte di form (elenco server e pulsanti), passando l'elenco dei server
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
# Apertura della pagina di table locks
#---------------------------------------	
@app.route('/table_locks', methods=('GET', 'POST'))
def table_locks():
	global v_elenco_tabelle

	# importa librerie necessarie
	from table_locks import table_locks_class
	from table_locks import ricerca_blocchi_tabella
	from utilita_database import estrae_elenco_tabelle_oracle
	
	# carico la parte di form (elenco server e pulsanti), passando l'elenco dei server
	form = table_locks_class()
	# carico elenco dei server nel relativo campo
	form.e_server_name.choices = o_preferenze.elenco_server
	# carico elenco tabelle (uso della variabile "globale" per fare in modo di riprendere i valori)
	form.e_table_name.choices = v_elenco_tabelle

	# processo il post
	v_tab_html = ''
	if request.method == 'POST':
		e_server_name = form.e_server_name.data		
		e_table_name = form.e_table_name.data
		
		# è stato premuto il pulsante per caricare elenco delle tabelle 
		if request.form.get('b_carica_nomi_tabelle')=='click_b_carica_nomi_tabelle':
			v_elenco_tabelle = estrae_elenco_tabelle_oracle( '1','SMILE','SMILE',form.e_server_name.data ) 
			form.e_table_name.choices = v_elenco_tabelle
	
		# è stato richiesto di visualizzare gli oggetti invalidi
		if request.form.get('b_ricerca_blocchi'):
			if e_table_name != None:				
				v_tab_html = ricerca_blocchi_tabella(o_preferenze, e_server_name, e_table_name)			
	
	# restituisco la pagina
	return render_template('table_locks.html', 
							python_form=form, 
							python_elenco_righe=v_tab_html)								

#------------------------------------------------------------
# Apertura della pagina che visualizza elenco delle sessioni
#------------------------------------------------------------
@app.route('/sessions_list', methods=('GET', 'POST'))
def sessions_list():	
	# importa librerie necessarie
	from sessions_list import sessions_list_class
	from sessions_list import get_elenco_sessioni
	from sessions_list import get_totale_sessioni_per_utente
	
	# carico la parte di form (elenco server e pulsanti), passando l'elenco dei server
	form = sessions_list_class()
	# carico elenco dei server nel relativo campo
	form.e_server_name.choices = o_preferenze.elenco_server
	
	# processo il post	
	v_tab_html = ''	
	v_totale_sessioni = ''
	if request.method == 'POST':
		e_server_name = form.e_server_name.data				
		
		# è stato richiesto di caricare la lista
		if request.form.get('b_load_list'):			
			v_tab_html = get_elenco_sessioni(o_preferenze, e_server_name)			
			v_totale_sessioni = '. Total grouped by user name: ' + get_totale_sessioni_per_utente(o_preferenze, e_server_name)
	
	# restituisco la pagina
	return render_template('sessions_list.html', 
							python_form=form, 
							python_elenco_righe=v_tab_html,
							python_totale_sessioni=v_totale_sessioni)

#---------------------------------------------------
# Apertura della pagina che monitora occupazione DB
#---------------------------------------------------
@app.route('/top_sessions', methods=('GET', 'POST'))
def top_sessions():
	global o_top_sessions
	global v_data_start
	
	# importa librerie necessarie
	from top_sessions import form_top_sessions_class
	from top_sessions import elenco_parametri
	from top_sessions import oracle_top_sessions_class
	
	# carico la parte di form (elenco server e pulsanti), passando l'elenco dei server
	form = form_top_sessions_class()
	# carico elenco dei server nel relativo campo
	form.e_server_name.choices = o_preferenze.elenco_server
	# carico elenco dei parametri
	form.e_parameter.choices = elenco_parametri()
	
	# processo il post	
	v_tab_html = ''			
	if request.method == 'POST':
		e_server_name = form.e_server_name.data						
		e_parameter = form.e_parameter.data						
		# è stato richiesto di caricare la lista
		if request.form.get('b_compute'):
			# cambio titolo al pulsante
			form.b_compute.label.text='Compute difference'
			# controllo se o_top_sessions è già stata creata, se non lo è eseguo tutti gli step di inizializzazione
			# che si occupano di instanziare il programma, creare il punto di partenza ed estrarre la tabella
			if 'o_top_sessions' not in globals():
				print('Inizializzo top sessions')
				# mi salvo la data d'inizio per indicare all'utente il punto di start
				v_data_start = '. Start date: ' + str(datetime.datetime.now().strftime('%H:%M:%S') )				
				# inizializzo l'oggetto
				o_top_sessions = oracle_top_sessions_class(o_preferenze, e_server_name, e_parameter)				
				# eseguo lo starter (caricamento punto di partenza)
				o_top_sessions.starter()
				# estraggo, per la visualizzazione, il contenuto della pagina1				
				v_tab_html = o_top_sessions.load_screen(o_top_sessions.page1)						
			# l'inizializzazione è stata eseguita e quindi ora svolgo la differenza tra la fotografia di partenza e
			# lo stato attuale
			else:
				print('Calcolo differenze top sessions')
				# calcolo la differenza tra la pagina2 e la pagina1 e il risultato lo metto nella pagina 3
				# la pagina1 viene constestualmente aggiornata togliendo le sessioni chiuse e inserendo quelle nuove
				o_top_sessions.calc_differenze()
				# estraggo, per la visualizzazione, il contenuto della pagina1
				v_tab_html = o_top_sessions.load_screen(o_top_sessions.page1)						
	else:
		v_data_start = ''
	
	# restituisco la pagina
	return render_template('top_sessions.html', 
							python_form=form, 
							python_intestazione=v_data_start,
							python_elenco_righe=v_tab_html)

#---------------------------------------	
# Apertura della pagina di kill session
# questa pagina riceve i seguenti parametri: nome server, sid, serial number, nome della pagina di provenienza
#---------------------------------------	
@app.route('/session_kill', methods=('GET', 'POST'))
def session_kill():
	# importa la funzione per killare la sessione
	from utilita_database import killa_sessione
	
	# leggo i parametri (nome del server, sid, numero di serie, nome della pagina a cui ritornare)
	v_server = request.args.get('p_server')	
	v_sid = request.args.get('p_sid')	
	v_serial_n = request.args.get('p_serial')	
	v_page = request.args.get('p_page')	
	
	if request.method == 'POST':
		# è stato premuto il button close
		if request.form.get('b_close')=='click_b_close':
			return redirect(url_for(v_page))
		# è stato premuto il button kill
		if request.form.get('b_kill')=='click_b_kill':
			# chiudo la sessione
			v_ok = killa_sessione(
									v_sid, # colonna 0 della riga
									v_serial_n, # colonna 1 della riga
									o_preferenze.v_oracle_user_sys,
									o_preferenze.v_oracle_password_sys,
									v_server
								)    
			# emetto messaggio di successo
			if v_ok == 'ok':
				flash('The session is being closed.')
			# emetto eventuale errore (es. sessione non trovata)
			else:
				return v_ok
	
	# restituisco il rendering della pagina con numero di sid
	return render_template('session_kill.html', python_parametro_sid=v_sid)

#---------------------------------------	
# Apertura della pagina di session info
# questa pagina riceve i seguenti parametri: nome server, sid, serial number, nome della pagina di provenienza
#---------------------------------------	
@app.route('/session_info')
def session_info():
	# importa la funzione per ottenere le info di sessione
	from utilita_database import informazioni_sessione
	
	# leggo i parametri (nome del server, sid, numero di serie, nome della pagina a cui ritornare)
	v_server = request.args.get('p_server')	
	v_sid = request.args.get('p_sid')	
	v_serial_n = request.args.get('p_serial')	
	v_page = request.args.get('p_page')	
	
	# info di sessione
	v_info_sessione = informazioni_sessione(
									v_sid, # colonna 0 della riga									
									o_preferenze.v_oracle_user_sys,
									o_preferenze.v_oracle_password_sys,
									v_server
									)    
	
	# restituisco il rendering della pagina
	return render_template('session_info.html', python_info_sessione=v_info_sessione)	

#---------------------------------------	
# Apertura della pagina ascii graphics generator
#---------------------------------------	
@app.route('/ascii_graphics', methods=('GET', 'POST'))
def ascii_graphics():
	# importa le funzioni di servizio alla pagina
	from ascii_graphics import ascii_graphics_class
	from ascii_graphics import converte_in_big_text

	# carico la parte di form (elenco fonts e pulsanti)
	form = ascii_graphics_class()

	# se premuto il pulsante di conferma procedo con la conversione
	v_testo_convertito = ''
	if request.method == 'POST' and request.form.get('b_esegue'):		
		v_testo_convertito = converte_in_big_text(form.e_fonts_list.data, form.e_converte.data)	
		
	# restituisco il rendering della pagina
	return render_template('ascii_graphics.html',
							python_form=form, 
							python_testo_convertito=v_testo_convertito)	

#---------------------------------------	
# Apertura della pagina download from server
#---------------------------------------	
@app.route('/download_from_server', methods=('GET', 'POST'))
def download_from_server():
	# importa le funzioni di servizio alla pagina
	from download_from_server import download_from_server_class	
	from download_from_server import execute_download_from_server

	# carico la parte di form (elenco fonts e pulsanti)
	form = download_from_server_class()

	# se premuto il pulsante di conferma procedo con la conversione	
	v_link = ''
	if request.method == 'POST' and request.form.get('b_esegue'):		
		v_link = execute_download_from_server(o_preferenze.v_server_password_iAS, form.e_source.data)
		if v_link != 'Error to download!' and v_link != '':
			return send_file(v_link, as_attachment=True)

	# restituisco il rendering della pagina
	return render_template('download_from_server.html',
							python_form=form,
							python_link_download=v_link)	

#---------------------------------------	
# Apertura della pagina elenco telefonico
#---------------------------------------	
@app.route('/books')
def books(): 	
	# importa librerie necessarie
	from books import load_rubrica
    
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