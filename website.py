from flask import Flask, request,render_template
import database

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def login():
    rform=request.form
    if request.method=='POST':
        email=rform['Email']
        password=rform['Passwort']
        login_message=database.accLogin(email,password)
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
        dbemails=database.readsql('accounts')
        if email in dbemails:
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
    return render_template('Index.j2')

@app.route('/hinzufügen',methods=['GET','POST'])
def hinzufügen():
    
    return render_template('Hinzufügen.j2')

@app.route('/lernen',methods=['GET','POST'])
def lernen():
    return render_template('Lernen.j2')

@app.route('/prüfen',methods=['GET','POST'])
def prüfen():
    return render_template('Prüfen.j2')

if __name__=='__main__':
    app.run()