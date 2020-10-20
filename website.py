from flask import Flask, request,render_template, session, flash
from flask_mail import Mail, Message
import database as db

app = Flask(__name__)
app.secret_key='(\x89\x8e\xc4\xa1\xf4\xfd\xce@\xaf\xe5\xf6'
mail=Mail(app)

def authentication():
    #funktioniert noch nicht D:
    if not session.get('logged_in'):
        return render_template('login.j2')

@app.route('/', methods=['GET','POST'])
def login():
    rform=request.form
    if request.method=='POST':
        email=rform['Email']
        password=rform['Passwort']
        login_bool=db.user_login(email,password)
        if login_bool==True:
            session['logged_in']=True
            return render_template('Home.j2')
        else:
            flash('Email oder Passwort falsch!')
    return render_template('login.j2')

@app.route('/pw-vergessen', methods=['GET','POST'])
def pw_vergessen():
    return render_template('pw_vergessen.j2')  

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    session['Admin']=False
    return render_template('login.j2')

# pw_validation=Passwortbestätigung
@app.route('/registrieren',methods=['GET','POST'])
def registrieren():
    # authentication()
    if not session.get('logged_in'):
        return render_template('login.j2')
    rform=request.form
    if request.method=='POST':
        email=rform['Email']
        password=rform['Passwort']
        pw_validation=rform['pw_validation']
        if password == pw_validation:
            db.user_regist(email,password)
            users=db.user_getall2Dict()
            return render_template('usermanagement.j2', users=users)     
        else:
            flash('Passwörter stimmen nicht überein!')
    return render_template('registrieren.j2')

@app.route('/home',methods=['GET','POST'])
def home():
    # authentication()
    if not session.get('logged_in'):
        return render_template('login.j2')
    return render_template('home.j2')

@app.route('/hinzufügen',methods=['GET','POST'])
def hinzufügen():
    # authentication()
    if not session.get('logged_in'):
        return render_template('login.j2')
    return render_template('hinzufügen.j2')

@app.route('/fragen',methods=['GET','POST'])
def fragen():
    # authentication()
    if not session.get('logged_in'):
        return render_template('login.j2')
    return render_template('fragen.j2')

@app.route('/admin_auth', methods=['GET','POST'])
def admin_auth():
    # authentication()
    if not session.get('logged_in'):
        return render_template('login.j2')
    if request.method=='POST':
        rform = request.form
        if 'pw' in rform:
            pw=rform['pw']
            admin_pw='123asdqweyxc'
            if pw != admin_pw:
                flash('Passwort ist falsch!')
            else:
                session['Admin']=True
                users=db.user_getall2Dict()
                return render_template('usermanagement.j2', users=users)
    return render_template('admin_auth.j2')

@app.route('/usermanagement', methods=['GET','POST'])
def usermanagement():
    # authentication()
    if not session.get('logged_in'):
        return render_template('login.j2')
    if not session.get('Admin'):
        return render_template('admin_auth.j2')
    if request.method=='POST':
        rform=request.form
        if "Button_del" in rform:
            print(db.user_delete(rform['Button_del']))
    users=db.user_getall2Dict()
    return render_template('usermanagement.j2', users=users)

if __name__=='__main__':
    app.run()