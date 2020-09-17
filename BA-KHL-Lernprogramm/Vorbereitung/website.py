from flask import Flask, request,render_template
import database

user="Owner"
password="Ownerpassword"

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def login():
    rform=request.form
    if request.method=='POST':
        email=rform['Email']
        password=rform['Passwort']
        login_val=database.accLogin(email,password)
        return render_template('Login.j2',login_val=login_val)
    return render_template('Login.j2')

@app.route('/registrieren',methods=['GET','POST'])
def registrieren():
    rform=request.form
    if request.method=='POST':
        email=rform['Email']
        password=rform['Passwort']
        pw_best=rform['pw_best']
        if password == pw_best:
            database.accRegister(email,password)
            pw_val='Erfolgreich registriert!'
            return render_template('Login.j2', pw_val=pw_val)       
        else:
            pw_val='Passwörter stimmen nicht überein!'
            return render_template('Registrieren.j2', pw_val=pw_val)
    return render_template('Registrieren.j2')

if __name__=='__main__':
    app.run()