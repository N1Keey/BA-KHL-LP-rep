from flask import Flask, request,render_template, session, flash
import os
import database

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def login():
    rform=request.form
    if request.method=='POST':
        email=rform['Email']
        password=rform['Passwort']
        accountdata=database.accLogin(email)
        accountstatus=accountdata[3]
        #accountdata[i], i=0 => ID, i=1=>Email, i=2=>Password, i=3=>Status
        if email==accountdata[1] and password==accountdata[2]:
            session['logged_in']=True
            return render_template('Index.j2',accountstatus=accountstatus)
        else:
            flash('Email oder Passwort falsch!')
        return render_template('Login.j2')
    return render_template('Login.j2')

# pw_validation=Passwortbestätigung
@app.route('/registrieren',methods=['GET','POST'])
def registrieren():
    rform=request.form
    if request.method=='POST':
        email=rform['Email']
        password=rform['Passwort']
        pw_validation=rform['pw_validation']
        dbemails=database.readAccounts(column=1)
        if email == dbemails[0]:
            flash('Email existiert schon!')
            return render_template('Registrieren.j2') 
        if password == pw_validation:
            database.accRegister(email,password)
            flash('Erfolgreich registriert!')
            return render_template('Login.j2')       
        else:
            flash('Passwörter stimmen nicht überein!')
            return render_template('Registrieren.j2')
    return render_template('Registrieren.j2')

@app.route('/index',methods=['GET','POST'])
def index():
    if not session.get('logged_in'):
        return render_template('Login.j2')
    return render_template('Index.j2')

@app.route('/hinzufügen',methods=['GET','POST'])
def hinzufügen():
    if not session.get('logged_in'):
        return render_template('Login.j2')
    return render_template('Hinzufügen.j2')

@app.route('/lernen',methods=['GET','POST'])
def lernen():
    if not session.get('logged_in'):
        return render_template('Login.j2')
    return render_template('Lernen.j2')

@app.route('/prüfen',methods=['GET','POST'])
def prüfen():
    if not session.get('logged_in'):
        return render_template('Login.j2')
    return render_template('Prüfen.j2')

if __name__=='__main__':
    app.secret_key = os.urandom(12)
    app.run()