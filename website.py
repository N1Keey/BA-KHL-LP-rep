from flask import Flask, request,render_template, session, flash 
import user_database

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def login():
    rform=request.form
    if request.method=='POST':
        email=rform['Email']
        password=rform['Passwort']
        login_bool=user_database.user_login(email,password)
        if login_bool==True:
            session['logged_in']=True
            return render_template('Home.j2')
        else:
            flash('Email oder Passwort falsch!')
    return render_template('login.j2')

# pw_validation=Passwortbestätigung
@app.route('/registrieren',methods=['GET','POST'])
def registrieren():
    rform=request.form
    if request.method=='POST':
        email=rform['Email']
        password=rform['Passwort']
        pw_validation=rform['pw_validation']
        if password == pw_validation:
            user_database.user_regist(email,password)
            flash('Erfolgreich registriert!')
            return render_template('login.j2')       
        else:
            flash('Passwörter stimmen nicht überein!')
    return render_template('registrieren.j2')

@app.route('/index',methods=['GET','POST'])
def index():
    if not session.get('logged_in'):
        return render_template('login.j2')
    return render_template('home.j2')

@app.route('/hinzufügen',methods=['GET','POST'])
def hinzufügen():
    if not session.get('logged_in'):
        return render_template('login.j2')
    return render_template('hinzufügen.j2')

@app.route('/lernen',methods=['GET','POST'])
def lernen():
    if not session.get('logged_in'):
        return render_template('login.j2')
    return render_template('lernen.j2')

@app.route('/prüfen',methods=['GET','POST'])
def prüfen():
    if not session.get('logged_in'):
        return render_template('login.j2')
    return render_template('prüfen.j2')

if __name__=='__main__':
    app.secret_key = '(\x89\x8e\xc4\xa1\xf4\xfd\xce@\xaf\xe5\xf6'
    app.run()