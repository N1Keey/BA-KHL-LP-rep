from flask import Flask, request,render_template, session
import os
import database

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def login():
    rform=request.form
    if request.method=='POST':
        email=rform['Email']
        password=rform['Passwort']
        login_bool=database.accLogin(email,password)
        if login_bool == True:
            session['logged_in']=True
            return render_template('Index.j2')
        else:
            login_message='Email oder Passwort falsch!'
        return render_template('Login.j2',login_message=login_message)
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
            regist_message='Email existiert schon!'
            return render_template('Login.j2', regist_message=regist_message) 
        if password == pw_validation:
            database.accRegister(email,password)
            regist_message='Erfolgreich registriert!'
            return render_template('Login.j2', regist_message=regist_message)       
        else:
            regist_message='Passwörter stimmen nicht überein!'
            return render_template('Registrieren.j2', regist_message=regist_message)
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