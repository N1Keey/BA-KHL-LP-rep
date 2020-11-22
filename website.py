from flask import Flask, request, render_template, redirect, session, flash
from flask_mail import Mail, Message
import database as db
from pprint import pprint

app = Flask(__name__)
app.secret_key='(\x89\x8e\xc4\xa1\xf4\xfd\xce@\xaf\xe5\xf6'

## Funzt nicht D:
# app.config.update(dict(
#     DEBUG = True,
#     MAIL_SERVER = 'smtp.gmail.com',
#     MAIL_PORT = 587,
#     MAIL_USE_TLS = True,
#     MAIL_USE_SSL = False,
#     MAIL_USERNAME = 'KHL.Usermanagement@gmail.com',
#     MAIL_PASSWORD = 'Passwort',
# ))

# mail=Mail(app)

@app.route('/', methods=['GET','POST'])
def login():
    rform=request.form
    if request.method=='POST':
        email=rform['Email']
        password=rform['Passwort']
        login_bool=db.User.login(email,password) #prüft, ob login daten mit db übereinstimmen gibt True oder False
        if login_bool==True:
            session['logged_in']=True
            return render_template('Home.j2')
        else:
            flash('Email oder Passwort falsch!')
    return render_template('login.j2')

@app.route('/pw-vergessen', methods=['GET','POST'])
def pw_vergessen():
    # if request.method == 'POST':
    #     rform=request.form
        # users=db.User.getall2Dict()
        # for user in users:
        #     if rform['Email'] == user['Email']:
        #         msg = Message("Hello",
        #           sender="KHL.Usermanagement@gmail.com",
        #           recipients=user['Email'])
        #         mail.send(msg)
    return render_template('pw_vergessen.j2')  

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    session['Admin']=False
    return redirect('/')

# pw_validation=Passwortbestätigung
@app.route('/registrieren',methods=['GET','POST'])
def registrieren():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform=request.form
        email=rform['Email']
        password=rform['Passwort']
        pw_validation=rform['pw_validation']
        if password == pw_validation:
            db.User.regist(email,password) #Registriert User mit Email und Passwort
            users=db.User.getall2Dict() #Speichert alle Daten der User in einem Dictionary
            return render_template('usermanagement.j2', users=users)     
        else:
            flash('Passwörter stimmen nicht überein!')
    return render_template('registrieren.j2')

@app.route('/home',methods=['GET','POST'])
def home():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('home.j2')

@app.route('/hinzufügen',methods=['GET','POST'])
def hinzufügen():
    if not session.get('logged_in'):
        return redirect('/')
    schemacontent=''
    message = '' #Message für User
    active_krankheit = session.get('active_krankheit') #Gerade Aktive Krankheit
    active_schema = session.get('active_schema') #Gerade Aktives Schema
    mode = session.get('mode') #Modus um bei Ursachen oder Komplikationen Krankheiten hinzuzufügen
    if request.method=='POST':
        rform=request.form
        if 'active_krankheit' in rform:
            active_krankheit=rform['active_krankheit']
            session['actives_schema']=''
            active_schema=''
        if 'active_krankheit' in rform and 'active_schema' in rform:
            active_schema=rform['active_schema']
        else:
            message='Zuerst Krankheit auswählen dann Eigenschaft'
    if active_schema=='Ursachen':
        kh_ursachen=db.Ursache.getAll_fromKrankheit(active_krankheit, True)
        schemacontent=kh_ursachen
    elif active_schema=='Symptome':
        kh_symptome=db.Symptom.getAll_fromKrankheit(active_krankheit, True)
        schemacontent=kh_symptome
    elif active_schema=='Komplikationen':
        kh_komplikationen=db.Komplikation.getAll_fromKrankheit(active_krankheit, True)
        schemacontent=kh_komplikationen
    elif active_schema=='Diagnostiken':
        kh_diagnostiken=db.Diagnostik.getAll_fromKrankheit(active_krankheit, True)
        schemacontent=kh_diagnostiken
    elif active_schema=='Therapien':
        kh_therapien=db.Therapie.getAll_fromKrankheit(active_krankheit, True)
        schemacontent=kh_therapien
    else:
        message='Links Krankheit auswählen und oben das Schema'
    krankheiten=db.Krankheit.getall()
    return render_template('hinzufügen.j2', krankheiten=krankheiten, active_schema=active_schema, 
    active_krankheit=active_krankheit, schemacontent=schemacontent, message=message, mode=mode)

@app.route('/hinzufügen_Krankheit', methods=['GET','POST'])
def hinzufügen_Krankheit():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform=request.form
        if 'Krankheit_name' in rform:
            name=rform['Krankheit_name']
            db.Krankheit.add(name)
    return redirect('/hinzufügen')

@app.route('/hinzufügen_Ursachen', methods=['GET','POST'])
def hinzufügen_Ursachen():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method == 'POST':
        rform = request.form
        active_krankheit=rform['active_krankheit']
        if 'kh_newUrsachen' in rform:
            if rform['kh_newUrsachen'] != '':
                ursache_name=rform['kh_newUrsachen']
                db.Ursache.add(active_krankheit, ursache_name) 
        session['active_schema']='Ursachen'
        session['active_krankheit']=active_krankheit
        if 'mode' in rform:
            if rform['mode']=='uok_Addkhmode' and session.get('mode')=='uok_Addkhmode':
                session['mode']=''
            else:
                session['mode']=rform['mode']
        elif 'uok_Addkh' in rform:
            session['mode']=''
            uok_addedkhs = request.form.getlist('checkbox_Krankheit')
            for uok_addedkh in uok_addedkhs:
                db.Ursache.addKrankheit(active_krankheit, uok_addedkh)
                db.Komplikation.addKrankheit(uok_addedkh,active_krankheit)
    return redirect('/hinzufügen')

@app.route('/hinzufügen_Symptome', methods=['GET','POST'])
def hinzufügen_symptome():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method == 'POST':
        rform = request.form
        active_krankheit=rform['active_krankheit']
        if rform['kh_newSymptome'] != '':
            symptom_name=rform['kh_newSymptome']
            db.Symptom.add(active_krankheit, symptom_name) 
        session['active_schema']='Symptome'
        session['active_krankheit']=active_krankheit
    return redirect('/hinzufügen')

@app.route('/hinzufügen_Komplikationen', methods=['GET','POST'])
def hinzufügen_Komplikationen():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method == 'POST':
        rform = request.form
        active_krankheit=rform['active_krankheit']
        if 'kh_newKomplikationen' in rform:
            if rform['kh_newKomplikationen'] != '':
                komplikation_name=rform['kh_newKomplikationen']
                db.Komplikation.add(active_krankheit, komplikation_name) 
        session['active_schema']='Komplikationen'
        session['active_krankheit']=active_krankheit
        if 'mode' in rform:
            if rform['mode']=='uok_Addkhmode' and session.get('mode')=='uok_Addkhmode':
                session['mode']=''
            else:
                session['mode']=rform['mode']
        elif 'uok_Addkh' in rform:
            session['mode']=''
            uok_addedkhs = request.form.getlist('checkbox_Krankheit')
            for uok_addedkh in uok_addedkhs:
                db.Komplikation.addKrankheit(active_krankheit, uok_addedkh)
                db.Ursache.addKrankheit(uok_addedkh, active_krankheit)
    return redirect('/hinzufügen')

@app.route('/hinzufügen_Diagnostiken', methods=['GET','POST'])
def hinzufügen_Diagnostiken():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method == 'POST':
        rform = request.form
        active_krankheit=rform['active_krankheit']
        if rform['kh_newDiagnostiken'] != '':
            diagnostik_name=rform['kh_newDiagnostiken']
            db.Diagnostik.add(active_krankheit, diagnostik_name) 
        session['active_schema']='Diagnostiken'
        session['active_krankheit']=active_krankheit
    return redirect('/hinzufügen')

@app.route('/hinzufügen_Therapien', methods=['GET','POST'])
def hinzufügen_Therapien():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method == 'POST':
        rform = request.form
        active_krankheit=rform['active_krankheit']
        if rform['kh_newTherapien'] != '':
            therapie_name=rform['kh_newTherapien']
            db.Therapie.add(active_krankheit, therapie_name) 
        session['active_schema']='Therapien'
        session['active_krankheit']=active_krankheit
    return redirect('/hinzufügen')

@app.route('/fragen',methods=['GET','POST'])
def fragen():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method == 'POST':
        rform = request.form
        if 'checkbox_Krankheit' in rform:
            if rform['checkbox_Krankheit'] != '':
                krankheiten4fragen = request.form.getlist('checkbox_Krankheit')
                krankheitendicts=db.Krankheit.getall2dict()
                fragendicts=[]
                for krankheitendict in krankheitendicts:
                    if krankheitendict['Krankheit'] in  krankheiten4fragen:
                        # for schema in krankheitdict:
                        ursachen=krankheitendict.get('Ursachen')
                        symptome=krankheitendict.get('Symptome')
                        komplikationen=krankheitendict.get('Komplikationen')
                        diagnostiken=krankheitendict.get('Diagnostiken')
                        therapien=krankheitendict.get('Therapien')     
    krankheiten=db.Krankheit.getall()
    return render_template('fragen.j2', krankheiten=krankheiten)

@app.route('/admin_auth', methods=['GET','POST'])
def admin_auth():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform = request.form
        if 'pw' in rform:
            pw=rform['pw']
            admin_pw='123asdqweyxc'
            if pw != admin_pw:
                flash('Passwort ist falsch!')
            else:
                session['Admin']=True
                users=db.User.getall2Dict()
                return render_template('usermanagement.j2', users=users)
    return render_template('admin_auth.j2')

@app.route('/usermanagement', methods=['GET','POST'])
def usermanagement():
    if not session.get('logged_in'):
        return redirect('/')
    if not session.get('Admin'):
        return redirect('/admin_auth')
    if request.method=='POST':
        rform=request.form
        if "Button_del" in rform:
            print(db.User.delete(rform['Button_del']))
    users=db.User.getall2Dict()
    return render_template('usermanagement.j2', users=users)

@app.route('/test', methods=['GET','POST'])
def test():
    return render_template('test.j2')

if __name__=='__main__':
    app.run()