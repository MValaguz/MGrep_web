echo off
echo +---------------------------------------------------------------------------------+
echo ! MGrep                                                                           !
echo !                                                                                 !
echo ! Avvio il server Flask che andra' in ascolto sulla porta http://10.0.47.9:5000/  !
echo ! (dove 5000 e' la porta di default e 10.0.47.9 e' l'indirizzo IP del mio PC)     !
echo +---------------------------------------------------------------------------------+
cd C:\Users\MValaguz\Documents\GitHub\MGrep_web\
set FLASK_APP=MGrep_web.py
set FLASK_ENV=development
python -m flask run --host=0.0.0.0
pause

