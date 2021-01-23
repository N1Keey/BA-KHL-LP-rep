from flask import Flask, request, render_template, redirect, session,send_file, flash
import database as db
import xml_export as xml
import json

app = Flask(__name__)
app.secret_key='(\x89\x8e\xc4\xa1\xf4\xfd\xce@\xaf\xe5\xf6'

@app.route('/', methods=['GET','POST'])
def login():
    rform=request.form
    if request.method=='POST':
        email=rform['Email']
        password=rform['Passwort']
        login_bool=db.User.login(email,password) #prüft, ob login daten mit db übereinstimmen gibt True oder False
        if login_bool==True:
            session['logged_in']=True
            return render_template('home.j2')
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

@app.route('/fragen',methods=['GET','POST'])
def fragen():
    if not session.get('logged_in'):
        return redirect('/')
    if session.get('fragenChanged'):
        fragenDicts=db.save_json2fragendicts()
    else:
        fragenDicts=[]
    cbx_checked=False
    if request.method == 'POST':
        rform = request.form
        if 'checkbox_Krankheit' in rform:
            if rform['checkbox_Krankheit'] != '':
                krankheiten4use = request.form.getlist('checkbox_Krankheit')
                fragenDicts=db.Frage.prepare_Dicts(krankheiten4use, 1)
                db.Frage.filldicts_withdata(fragenDicts, 1)
                db.Frage.builddicts_fromDatadicts(fragenDicts)
                db.save_fragendicts2json(fragenDicts)
        if 'cbx_allchecked' in rform:
            if rform.get('cbx_allchecked') == 'True':
                cbx_checked=False
            else:
                cbx_checked=True
        if 'exportdata' in rform:
            xml.create_file(db.save_json2fragendicts())
            export='Quizexport.xml'
            return send_file(export, as_attachment=True)
    krankheiten=db.Krankheit.getall()
    return render_template('fragen.j2', krankheiten=krankheiten, fragenDicts=fragenDicts, cbx_checked=cbx_checked)

@app.route('/fragen_update',methods=['GET','POST'])
def fragen_update():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method == 'POST':
        rform = request.form
        update=rform.get('fragenupdate')
        delete=json.loads(update)
        _krankheit=delete.get('krankheit')
        _umstand=delete.get('umstand')
        fragenDicts=db.save_json2fragendicts()
        for krankheit in fragenDicts:
            if krankheit.get('Krankheit')==_krankheit:
                krankheit.get('Umstände')[_umstand]=[]  
                db.Frage.filldicts_withdata(fragenDicts, 1)  
                db.Frage.builddicts_fromDatadicts(fragenDicts)  
                db.save_fragendicts2json(fragenDicts)
    session['fragenChanged']=True
    return redirect('/fragen')

@app.route('/fragen_delete',methods=['GET','POST'])
def fragen_delete():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method == 'POST':
        rform = request.form
        delete=rform.get('fragendelete')
        delete=json.loads(delete)
        krankheit=delete.get('krankheit')
        umstand=delete.get('umstand')
        fragendicts=db.save_json2fragendicts()
        for fragenkh in fragendicts:
            if fragenkh.get('Krankheit') == krankheit:
                fragenkh.pop(umstand)
        db.save_fragendicts2json(fragendicts)
    session['fragenChanged']=True
    return redirect('/fragen')

@app.route('/fragen2xml', methods=['GET','POST'])
def fragen2xml():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform=request.form
        if "exportdata" in rform:
            data=session.get('choice4exp')
            print(data)
    return redirect('/fragen')

@app.route('/stoff',methods=['GET','POST'])
def stoff():
    if not session.get('logged_in'):
        return redirect('/')
    umstandcontent=''
    message = '' #Message für User
    active_krankheit = session.get('active_krankheit') #Gerade Aktive Krankheit
    active_umstand = session.get('active_umstand') #Gerade Aktiver Umstand
    mode = session.get('mode') #Modus um bei Ursachen oder Komplikationen Krankheiten hinzuzufügen 
    element2change=''
    element2delete=''
    if request.method=='POST':
        rform=request.form
        if rform.get('active_krankheit')!='None':
            active_krankheit=rform.get('active_krankheit')
            session['actives_umstand']=''
            active_umstand=''
        if 'active_krankheit' in rform and 'active_umstand' in rform:
            active_umstand=rform['active_umstand']
        if 'ändern' in rform:
            element2change=rform.get('ändern')
        elif 'löschen' in rform:
            element2delete=rform.get('löschen')
        else:
            message='Zuerst Krankheit auswählen dann Eigenschaft'
    if active_umstand=='Ursachen':
        kh_ursachen=db.Ursache.getAll_fromKrankheit(db.Ursache,active_krankheit, True)
        umstandcontent=kh_ursachen
    elif active_umstand=='Symptome':
        kh_symptome=db.Symptom.getAll_fromKrankheit(db.Symptom,active_krankheit, True)
        umstandcontent=kh_symptome
    elif active_umstand=='Komplikationen':
        kh_komplikationen=db.Komplikation.getAll_fromKrankheit(db.Komplikation,active_krankheit, True)
        umstandcontent=kh_komplikationen
    elif active_umstand=='Diagnostiken':
        kh_diagnostiken=db.Diagnostik.getAll_fromKrankheit(db.Diagnostik,active_krankheit, True)
        umstandcontent=kh_diagnostiken
    elif active_umstand=='Therapien':
        kh_therapien=db.Therapie.getAll_fromKrankheit(db.Therapie,active_krankheit, True)
        umstandcontent=kh_therapien
    elif element2change!='' or element2delete!='':
        pass
    else:
        message='Links Krankheit auswählen und oben den Umstand'
    krankheiten=db.Krankheit.getall()
    krankheitendict=db.Krankheit.getall2dict()
    return render_template('stoff.j2', krankheiten=krankheiten, active_umstand=active_umstand, 
    active_krankheit=active_krankheit, umstandcontent=umstandcontent, message=message, mode=mode, 
    element2change=element2change, element2delete=element2delete, krankheitendict=krankheitendict)

@app.route('/suche', methods=['GET','POST'])
def suche():
    if not session.get('logged_in'):
        return redirect('/')
    suchelement=''
    foundkrankheitendict=[]
    if request.method=='POST':
        rform=request.form
        if rform.get('searchfield')!='':
            suchelement=rform.get('searchfield')
            krankheitendict=db.Krankheit.getall2dict()
            for krankheit in krankheitendict:
                for umstand in krankheit:
                    for element in krankheit.get(umstand):
                        if element.lower()==suchelement.lower():
                            foundelement=element
                            foundkrankheitdict={'Krankheit':krankheit.get('Krankheit'),'Umstand':umstand}
                            foundkrankheitendict.append(foundkrankheitdict)
    return render_template('suchseite.j2', foundelement=foundelement, foundkrankheitendict=foundkrankheitendict)

@app.route('/hinzufügen_Krankheit', methods=['GET','POST'])
def hinzufügen_Krankheit():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform=request.form
        if 'Krankheit_name' in rform:
            name=rform['Krankheit_name']
            db.Krankheit.add(name)
    return redirect('/stoff')

@app.route('/ändern_Krankheit', methods=['GET','POST'])
def ändern_Krankheit():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform=request.form
        db.Krankheit.change(rform.get('active_krankheit'), rform.get('elemupdate'))
    return redirect('/stoff')

@app.route('/löschen_Krankheit', methods=['GET','POST'])
def löschen_Krankheit():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform=request.form
        db.Krankheit.delete(rform.get('active_krankheit'))
    return redirect('/stoff')

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
                db.Ursache.add(db.Ursache, active_krankheit, ursache_name) 
        session['active_umstand']='Ursachen'
        session['active_krankheit']=active_krankheit
        if 'mode' in rform:
            if rform['mode']=='uok_Addkhmode' and session.get('mode')=='uok_Addkhmode':
                session['mode']=''
            else:
                session['mode']=rform['mode']
        elif 'uok_Addkh' in rform:
            session['mode']=''
            khs2add = request.form.getlist('checkbox_Krankheit')
            for kh2add in khs2add:
                db.Ursache.addKrankheit(db.Ursache,active_krankheit, kh2add)
                db.Komplikation.addKrankheit(db.Komplikation,kh2add,active_krankheit)
    return redirect('/stoff')

@app.route('/ändern_Ursachen', methods=['GET','POST'])
def ändern_Ursachen():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform = request.form
        content = rform.get('content')
        update = rform.get('elemupdate')
        active_krankheit=rform.get('active_krankheit')
        session['active_krankheit']=active_krankheit
        active_umstand=rform.get('active_umstand')
        session['active_umstand']=active_umstand
        if 'ch_alle' in rform:
            db.Ursache.changeall(db.Ursache, content, update)
        if 'ch_nurdieses' in rform:
            db.Ursache.changeone(db.Ursache, active_krankheit,content,update)
    return redirect('/stoff')

@app.route('/löschen_Ursachen', methods=['GET','POST'])
def löschen_Ursachen():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform = request.form
        content = rform.get('content')
        active_krankheit=rform.get('active_krankheit')
        session['active_krankheit']=active_krankheit
        active_umstand=rform.get('active_umstand')
        session['active_umstand']=active_umstand
        if 'del_alle' in rform:
            db.Umstand.deleteall(db.Ursache, content)
        if 'del_nurdieses' in rform:
            db.Ursache.deleteone(db.Ursache, active_krankheit, content)
    return redirect('/stoff')

@app.route('/hinzufügen_Symptome', methods=['GET','POST'])
def hinzufügen_Symptome():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method == 'POST':
        rform = request.form
        active_krankheit=rform['active_krankheit']
        if rform['kh_newSymptome'] != '':
            symptom_name=rform['kh_newSymptome']
            db.Symptom.add(db.Symptom, active_krankheit, symptom_name) 
        session['active_umstand']='Symptome'
        session['active_krankheit']=active_krankheit
    return redirect('/stoff')

@app.route('/ändern_Symptome', methods=['GET','POST'])
def ändern_Symptome():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform = request.form
        content = rform.get('content')
        update = rform.get('elemupdate')
        active_krankheit=rform.get('active_krankheit')
        session['active_krankheit']=active_krankheit
        active_umstand=rform.get('active_umstand')
        session['active_umstand']=active_umstand
        if 'ch_alle' in rform:
            db.Symptom.changeall(db.Symptom, content, update)
        if 'ch_nurdieses' in rform:
            db.Symptom.changeone(db.Symptom, active_krankheit,content,update)
    return redirect('/stoff')

@app.route('/löschen_Symptome', methods=['GET','POST'])
def löschen_Symptome():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform = request.form
        content = rform.get('content')
        active_krankheit=rform.get('active_krankheit')
        session['active_krankheit']=active_krankheit
        active_umstand=rform.get('active_umstand')
        session['active_umstand']=active_umstand
        if 'del_alle' in rform:
            db.Symptom.deleteall(db.Symptom, content)
        if 'del_nurdieses' in rform:
            db.Symptom.deleteone(db.Symptom, active_krankheit, content)
    return redirect('/stoff')

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
                db.Komplikation.add(db.Komplikation, active_krankheit, komplikation_name) 
        session['active_umstand']='Komplikationen'
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
                db.Komplikation.addKrankheit(db.Komplikation,active_krankheit, uok_addedkh)
                db.Ursache.addKrankheit(db.Ursache,uok_addedkh, active_krankheit)
    return redirect('/stoff')

@app.route('/ändern_Komplikationen', methods=['GET','POST'])
def ändern_Komplikationen():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform = request.form
        content = rform.get('content')
        update = rform.get('elemupdate')
        active_krankheit=rform.get('active_krankheit')
        session['active_krankheit']=active_krankheit
        active_umstand=rform.get('active_umstand')
        session['active_umstand']=active_umstand
        if 'ch_alle' in rform:
            db.Komplikation.changeall(db.Komplikation, content,update)
        if 'ch_nurdieses' in rform:
            db.Komplikation.changeone(db.Komplikation, active_krankheit,content,update)
    return redirect('/stoff')

@app.route('/löschen_Komplikationen', methods=['GET','POST'])
def löschen_Komplikationen():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform = request.form
        content = rform.get('content')
        active_krankheit=rform.get('active_krankheit')
        session['active_krankheit']=active_krankheit
        active_umstand=rform.get('active_umstand')
        session['active_umstand']=active_umstand
        if 'del_alle' in rform:
            db.Komplikation.deleteall(db.Komplikation, content)
        if 'del_nurdieses' in rform:
            db.Komplikation.deleteone(db.Komplikation, active_krankheit,content)

    return redirect('/stoff')

@app.route('/hinzufügen_Diagnostiken', methods=['GET','POST'])
def hinzufügen_Diagnostiken():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method == 'POST':
        rform = request.form
        active_krankheit=rform['active_krankheit']
        if rform['kh_newDiagnostiken'] != '':
            diagnostik_name=rform['kh_newDiagnostiken']
            db.Diagnostik.add(db.Diagnostik, active_krankheit, diagnostik_name) 
        session['active_umstand']='Diagnostiken'
        session['active_krankheit']=active_krankheit
    return redirect('/stoff')

@app.route('/ändern_Diagnostiken', methods=['GET','POST'])
def ändern_Diagnostiken():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform = request.form
        content = rform.get('content')
        update = rform.get('elemupdate')
        active_krankheit=rform.get('active_krankheit')
        session['active_krankheit']=active_krankheit
        active_umstand=rform.get('active_umstand')
        session['active_umstand']=active_umstand
        if 'ch_alle' in rform:
            db.Diagnostik.changeall(db.Diagnostik, content,update)
        if 'ch_nurdieses' in rform:
            db.Diagnostik.changeone(db.Diagnostik, active_krankheit,content,update)
    return redirect('/stoff')

@app.route('/löschen_Diagnostiken', methods=['GET','POST'])
def löschen_Diagnostiken():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform = request.form
        content = rform.get('content')
        active_krankheit=rform.get('active_krankheit')
        session['active_krankheit']=active_krankheit
        active_umstand=rform.get('active_umstand')
        session['active_umstand']=active_umstand
        if 'del_alle' in rform:
            db.Diagnostik.deleteall(db.Diagnostik, content)
        if 'del_nurdieses' in rform:
            db.Diagnostik.deleteone(db.Diagnostik, active_krankheit, content)
    return redirect('/stoff')

@app.route('/hinzufügen_Therapien', methods=['GET','POST'])
def hinzufügen_Therapien():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method == 'POST':
        rform = request.form
        active_krankheit=rform['active_krankheit']
        if rform['kh_newTherapien'] != '':
            therapie_name=rform['kh_newTherapien']
            db.Therapie.add(db.Therapie, active_krankheit, therapie_name) 
        session['active_umstand']='Therapien'
        session['active_krankheit']=active_krankheit
    return redirect('/stoff')

@app.route('/ändern_Therapien', methods=['GET','POST'])
def ändern_Therapien():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform = request.form
        content = rform.get('content')
        update = rform.get('elemupdate')
        active_krankheit=rform.get('active_krankheit')
        session['active_krankheit']=active_krankheit
        active_umstand=rform.get('active_umstand')
        session['active_umstand']=active_umstand
        if 'ch_alle' in rform:
            db.Therapie.changeall(db.Therapie, content,update)
        if 'ch_nurdieses' in rform:
            db.Therapie.changeone(db.Therapie, active_krankheit, content, update)
    return redirect('/stoff')

@app.route('/löschen_Therapien', methods=['GET','POST'])
def löschen_Therapien():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method=='POST':
        rform = request.form
        content = rform.get('content')
        active_krankheit=rform.get('active_krankheit')
        session['active_krankheit']=active_krankheit
        active_umstand=rform.get('active_umstand')
        session['active_umstand']=active_umstand
        if 'del_alle' in rform:
            db.Therapie.deleteall(db.Therapie, content)
        if 'del_nurdieses' in rform:
            db.Therapie.deleteone(db.Therapie, active_krankheit,content)
    return redirect('/stoff')

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
    #app.run(host='0.0.0.0', port=5000)