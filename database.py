from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Table, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json
import random
import math

engine = create_engine('sqlite:///khl_lp.db',connect_args={'check_same_thread': False})

connection=engine.connect()
Base=declarative_base()
Session= sessionmaker(bind=engine)
session=Session()

# Many2Many Relation zwischen users und roles
roles_users = Table('roles_users',Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE")),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete="CASCADE"))
    )

class User(Base):
    __tablename__='users'

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(255))
    roles = relationship('Role', secondary=roles_users) # bei Anfrage bezug auf roles_users -> Relationtable  
    
    def regist(user_email, user_password):
        """Adds User to Database and gives the standard-role: 'User'
        """
        new_User=User(email=user_email, password=user_password)
        new_user_role=session.query(Role).filter(Role.name=='User').first()
        new_User.roles=[new_user_role]
        session_add_and_commit(new_User)

    def login(user_email, user_password):
        """returns True if Email exists and Password is right
        False if Email isnt existing or Password isnt right
        """
        login_bool=False
        users=session.query(User)
        for user in users:
            if user_email==user.email and user_password==user.password:
                login_bool=True
        return login_bool

    def getall2Dict():
        """Returns Userdata of all Users with roles in a list of Dictionarys
        {'ID':user.id,'Email':user.email,'Password':user.password,'Roles':userrolelist}
        """
        userdicts=[]
        users=session.query(User).join(User.roles).all()
        for user in users:
            userrolelist=[]
            for role in user.roles:
                userrolelist.append(role.name) 
            userdict={'ID':user.id,'Email':user.email,'Password':user.password,'Roles':userrolelist}
            userdicts.append(userdict)  
        return userdicts

    def delete(user_ID):
        """Deletes User with given user_ID"""
        user=session.query(User).filter(User.id==user_ID)
        if user.first().email != 'Nschick@mail.hs-ulm.de':
            user.delete()
            session.commit()

class Role(Base):
    __tablename__='roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)
    description = Column(String(255))

    def add(role_name, role_description):
        """Adds Role to Database"""
        new_Role=Role(name=role_name, description=role_description)
        session_add_and_commit(new_Role)

    def role2User(user_email, role_name):
        """Adds Role with role_name to User with user_email"""
        user_roles=[]
        user=session.query(User).join(User.roles).filter(User.email==user_email).first()
        for role in user.roles:
            user_roles.append(role)
        new_user_role=session.query(Role).filter(Role.name==role_name).first()
        user_roles.append(new_user_role)
        user.roles=user_roles
        session.commit()

kh2ursache = Table('kh2ursache', Base.metadata,
    Column('krankheit_id', Integer, ForeignKey('krankheit.id', ondelete="CASCADE")),
    Column('ursache_id', Integer, ForeignKey('ursache.id', ondelete="CASCADE")),
    )
kh2symptom = Table('kh2symptom', Base.metadata,
    Column('krankheit_id', Integer, ForeignKey('krankheit.id', ondelete="CASCADE")),
    Column('symptom_id', Integer, ForeignKey('symptom.id', ondelete="CASCADE")),
    )
kh2komplikation = Table('kh2komplikation', Base.metadata,
    Column('krankheit_id', Integer, ForeignKey('krankheit.id', ondelete="CASCADE")),
    Column('komplikation_id', Integer, ForeignKey('komplikation.id', ondelete="CASCADE")),
    )
kh2diagnostik = Table('kh2diagnostik', Base.metadata,
    Column('krankheit_id', Integer, ForeignKey('krankheit.id', ondelete="CASCADE")),
    Column('diagnostik_id', Integer, ForeignKey('diagnostik.id', ondelete="CASCADE")),
    )
kh2therapie = Table('kh2therapie', Base.metadata,
    Column('krankheit_id', Integer, ForeignKey('krankheit.id', ondelete="CASCADE")),
    Column('therapie_id', Integer, ForeignKey('therapie.id', ondelete="CASCADE"))
    )


class Krankheit(Base):
    __tablename__='krankheit'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)
    ursachen = relationship('Ursache', secondary=kh2ursache)
    symptome = relationship('Symptom', secondary=kh2symptom)
    komplikationen = relationship('Komplikation', secondary=kh2komplikation)
    diagnostiken = relationship('Diagnostik', secondary=kh2diagnostik)
    therapien = relationship('Therapie', secondary=kh2therapie)

    def add(krankheit_name):
        """Adds Krankheiten 2 db"""
        new_Krankheit=Krankheit(name=krankheit_name)
        session_add_and_commit(new_Krankheit)

    def getall():
        """Get all Krankheiten
        returns sqlelements"""
        krankheiten=[]
        sqlelement=session.query(Krankheit).order_by(Krankheit.id.asc()).all()
        for row in sqlelement:
            krankheiten.append(row.name)
        return krankheiten

    def getall2dict():
        """Alle Krankheiten mit Umständen als Liste von Dicts
        Dict: 
        [{
            'Krankheit':krankheit.name, 'Umstände':{
            "Ursachen":ursachen, "Symptome":symptome, "Komplikationen":komplikationen, "Diagnostiken":diagnostiken, "Therapien":therapien
        }}]"""
        krankheiten=session.query(Krankheit).all()
        krankheitendicts=[]
        for krankheit in krankheiten:
            krankheitendict={'Krankheit':krankheit.name, 'Umstände':{}}
            ursachen=Umstand.getAll_fromKrankheit(Ursache, krankheit.name, True)
            krankheitendict.get('Umstände')['Ursachen']=ursachen
            symptome=Umstand.getAll_fromKrankheit(Symptom, krankheit.name, True)
            krankheitendict.get('Umstände')['Symptome']=symptome
            komplikationen=Umstand.getAll_fromKrankheit(Komplikation, krankheit.name, True)
            krankheitendict.get('Umstände')['Komplikationen']=komplikationen
            diagnostiken=Umstand.getAll_fromKrankheit(Diagnostik, krankheit.name, True)
            krankheitendict.get('Umstände')['Diagnostiken']=diagnostiken
            therapien=Umstand.getAll_fromKrankheit(Therapie, krankheit.name, True)
            krankheitendict.get('Umstände')['Therapien']=therapien
            krankheitendicts.append(krankheitendict)
        return krankheitendicts  

    def change(krankheit_name, new_name):
        """
        krankheit_name = alter Name der Krankheit
        new_name = neuer Name für Krankheit
        """
        element2change=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
        element2change.name=new_name
        session_add_and_commit(element2change)       
    
    def delete(krankheit_name):
        """löscht Krankheit mit dem Namen: krankheit_name"""
        element2delete=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
        session.delete(element2delete)
        session.commit()

    def countelements():
        """zählt Krankheiten"""
        nKrankheiten = session.query(Krankheit.id).count()
        return nKrankheiten

class Umstand(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

    def add(_class, krankheit_name, element_name):
        """fügt Element mit element_name in Krankheit mit krankheit_name in den Umstand _class ein """
        if issubclass(_class, Umstand):
            element=session.query(_class).filter(_class.name==element_name).first() #query1 umstandelement
            if element is None:
                element=_class(name=element_name) #2 anlegen von umstandelement falls noch nicht vorhanden
                session_add_and_commit(element)
            krankheit_elemente=_class.getAll_fromKrankheit(_class, krankheit_name, False) #3 get all umstandelements von kh
            krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first() #4 query krankheit
            krankheit_elemente.append(element) #5 füge neues Element zu alten hinzu 
            setkh_Umstand_elemente(_class.__name__, krankheit, krankheit_elemente)
            session.commit()
        else:
            pass # Fehlermeldung

    def getAll(_class):
        """returns Alle Elemente des Umstands _class"""
        if issubclass(_class, Umstand):
            elemente=[]
            elementesql=session.query(_class).all()
            for element in elementesql:
                if element.name==None: # => element = Krankheit
                    element=session.query(Krankheit).filter(Krankheit.id==element.krankheit_id).first() # element = Krankheit
                elemente.append(element.name) # Namestrings
            return elemente
        else:
            pass # Fehlermeldung

    def getAll_fromKrankheit(_class, krankheit_name, toString=False):
        ''' _class => Umstand 
            toString = True => returns Namestrings
            toString = False => returns sqlelements 
        '''
        if issubclass(_class, Umstand):
            krankheit_elemente=[]
            joint=getkhJoint(_class.__name__)
            krankheit=joint.filter(Krankheit.name==krankheit_name).first()
            if krankheit is not None:
                krankheit_umstände=getkh_umstände(_class.__name__,krankheit)
                for element in krankheit_umstände:
                    krankheit_elemente.append(element)
                if toString==True:
                    elementstrings=[]
                    for element in krankheit_elemente:
                        if element.name is None: #element = Krankheit
                            element=session.query(Krankheit).filter(Krankheit.id==element.krankheit_id).first()
                        if element is not None:  
                            elementstrings.append(element.name)
                    krankheit_elemente=elementstrings
            return krankheit_elemente
        else:
            pass # Fehlermeldung

    def changeall(_class, element_name, newElement_name):
        """Ändert den Namen eines Elements"""
        if issubclass(_class, Umstand):
            element2change=session.query(_class).filter(_class.name==element_name).first()
            if element2change is not None: #None=> element2change = Krankheit
                element2change.name=newElement_name
                session_add_and_commit(element2change)                
            else:
                krankheit=session.query(Krankheit).filter(Krankheit.name==element_name).first()
                krankheit.name=newElement_name
            session.commit()
        else:
            pass # Fehlermeldung

    def changeone(_class, krankheit_name, element_name, newElement_name):
        """Ändert das Element element_name der Krankheit krankheit_name
            in newElement_name
        """
        if issubclass(_class, Umstand):
            _classquery=session.query(_class)
            kh_query=session.query(Krankheit)
            element=_classquery.filter(_class.name==element_name).first()
            krankheit_elemente=_class.getAll_fromKrankheit(_class, krankheit_name, False)
            krankheit_old=kh_query.filter(Krankheit.name==element_name).first()
            if element is None: #None => element=Krankheit
                element=_classquery.filter(_class.krankheit_id==krankheit_old.id).first()
            krankheit_elemente.remove(element) #entfernt das Element von Krankheit
            krankheit=kh_query.filter(Krankheit.name==krankheit_name).first()
            new_kh_element=kh_query.filter(Krankheit.name==newElement_name).first()
            if new_kh_element is None: # new_element != Krankheit
                new_element=_classquery.filter(_class.name==newElement_name).first()
                if new_element is None: # new_element gibts noch nicht in DB
                    new_element=_class(name=newElement_name)  # -> wird neu angelegt
            else:
                new_element=new_kh_element       
            krankheit_elemente.append(new_element)
            setkh_Umstand_elemente(_class.__name__, krankheit, krankheit_elemente)
            session.commit()
        else:
            pass # Fehlermeldung

    def deleteall(_class, element_name):
        """lösche Element aus DB"""
        if issubclass(_class, Umstand):
            element2delete=session.query(_class).filter(_class.name==element_name).first()
            if element2delete is None: #=> element2delete=Krankheit
                element2delete=session.query(Krankheit).filter(Krankheit.name==element_name).first()   
            session.delete(element2delete)
            session.commit()
        else:
            pass # Fehlermeldung

    def deleteone(_class, krankheit_name, element2del_name):
        """Entferne Element aus Krankheit"""
        if issubclass(_class, Umstand):
            _classquery=session.query(_class)
            kh_query=session.query(Krankheit)
            element2del=_classquery.filter(_class.name==element2del_name).first()
            krankheit_elemente=Umstand.getAll_fromKrankheit(_class, krankheit_name, False)
            krankheit=kh_query.filter(Krankheit.name==krankheit_name).first()
            if element2del is not None:
                krankheit_elemente.remove(element2del)
            else:
                krankheit2del=kh_query.filter(Krankheit.name==element2del_name).first()
                element_kh=_classquery.filter(_class.krankheit_id==krankheit2del.id).first()
                krankheit_elemente.remove(element_kh)
            setkh_Umstand_elemente(_class.__name__, krankheit, krankheit_elemente)
            session.commit()
        else:
            pass # Fehlermeldung

    def elementsearch(element2look4):
        """returns Dict
        Dict={'Foundelement':'', 'Hideouts':[{'Krankheit':krankheit.get('Krankheit'),'Umstand':umstand}]}
        """
        krankheitendict=Krankheit.getall2dict()
        foundkrankheitendict={'Foundelement':'', 'Hideouts':[]}
        for krankheit in krankheitendict:
            for umstand in krankheit.get('Umstände'):
                for element in krankheit.get('Umstände').get(umstand):
                    if element.lower()==element2look4.lower():
                        foundelement=element
                        foundkrankheitendict['Foundelement']=foundelement
                        hideout={'Krankheit':krankheit.get('Krankheit'),'Umstand':umstand}
                        foundkrankheitendict.get('Hideouts').append(hideout)         
        if foundkrankheitendict.get('Foundelement')=='':
            foundkrankheitendict['Foundelement']=element2look4
        return foundkrankheitendict

    def countelements(_class):
        """zählt Elemente des Umstands _class"""
        nUmstand = session.query(_class.id).count()
        return nUmstand

    __mapper_args__ = {
    'polymorphic_identity':'umstand',
    'polymorphic_on':type
    }

class VerknüpfenderUmstand(Umstand):
    __abstract__ = True
    krankheit_id = Column(Integer, unique=True)       

    def addKrankheit(_class, krankheit_name, krankheit2add):
        """fügt eine Krankheit hinzu"""
        if issubclass(_class, VerknüpfenderUmstand):
            if krankheit_name!=krankheit2add:
                kh_query=session.query(Krankheit)
                krankheit=kh_query.filter(Krankheit.name==krankheit2add).first()
                element_kh=session.query(_class).filter(_class.krankheit_id==krankheit.id).first()
                if element_kh is None: #Krankheit gibts noch nicht
                    element_kh=_class(krankheit_id=krankheit.id)
                    session_add_and_commit(element_kh)
                krankheit_elemente=VerknüpfenderUmstand.getAll_fromKrankheit(_class,krankheit_name, False)
                krankheit=kh_query.filter(Krankheit.name==krankheit_name).first()
                krankheit_elemente.append(element_kh)
                setkh_Umstand_elemente(_class.__name__,krankheit,krankheit_elemente)
                session.commit()
        else:
            pass # Fehlermeldung

    __mapper_args__ = {
    'polymorphic_identity':'verknüpfenderumstand',
    'polymorphic_on':type
    }

class Ursache(VerknüpfenderUmstand):
    __tablename__='ursache'

    __mapper_args__ = {
    'polymorphic_identity':'ursache',
    }

class Symptom(Umstand):
    __tablename__='symptom'
    
    __mapper_args__ = {
    'polymorphic_identity':'symptom',
    }
    
class Komplikation(VerknüpfenderUmstand):
    __tablename__='komplikation'

    __mapper_args__ = {
    'polymorphic_identity':'komplikation',
    }
    
class Diagnostik(Umstand):
    __tablename__='diagnostik'

    __mapper_args__ = {
    'polymorphic_identity':'diagnostik',
    }
    
class Therapie(Umstand):
    __tablename__='therapie'

    __mapper_args__ = {
    'polymorphic_identity':'therapie',
    }

Base.metadata.create_all(engine)

class Frage():
    nAntworten=6
    def kh2umstand_prepare_Dicts(krankheiten4use):
        """krankheiten4use => jeder Umstand (=5 Umstände)
            Fragentyp 1 und 2
        => pro Krankheit 10 Dicts
        """
        def prepare_kh2umstand(fragentyp):
            """baut die Dictionarys auf"""
            krankheitenfragendict={'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
            'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}
            return krankheitenfragendict
        krankheitenfragendicts=[]
        for krankheit in krankheiten4use:
            krankheitenfragendicts.append(prepare_kh2umstand(1))
            krankheitenfragendicts.append(prepare_kh2umstand(2))
        return krankheitenfragendicts
    def kh2umstand_filldicts_withdata(krankheitendicts4fragen, update=False):
        """füllt die vorbereiteten Dicts mit Daten
        update=False => Alle Daten werden neu generiert
        update=True => Nur Fehlende Daten werden neu generiert
        """
        def fill(krankheit,umstand):
            """Füllt umstand d. krankheit mit richtigen und falschen Elementen
            {'Frage':'','Antworten':{'Right':[],'Wrong':[]}}
            """
            krankheit.get('Umstände')[umstand]={'Frage':'','Antworten':{'Right':[],'Wrong':[]}}
            (umstandAll, umstandRights)=decide_umstand(krankheit,umstand)
            for element in umstandRights:
                krankheit.get('Umstände')[umstand]['Antworten']['Right'].append(element)
                if element in umstandAll:
                    umstandAll.remove(element)
            for element in umstandAll:
                krankheit.get('Umstände')[umstand]['Antworten']['Wrong'].append(element)           
        def decide_umstand(krankheit,umstand):
            """gibt je nach Krankheit und Umstand die richtigen und falschen Antworten zurück"""
            if umstand=='Ursachen':
                umstandRights=Ursache.getAll_fromKrankheit(Ursache,krankheit.get('Krankheit'), True)
                umstandAll=Ursache.getAll(Ursache)
            elif umstand=='Symptome':
                umstandRights=Symptom.getAll_fromKrankheit(Symptom,krankheit.get('Krankheit'), True)
                umstandAll=Symptom.getAll(Symptom)
            elif umstand=='Komplikationen':
                umstandRights=Komplikation.getAll_fromKrankheit(Komplikation,krankheit.get('Krankheit'), True)
                umstandAll=Komplikation.getAll(Komplikation)
            elif umstand=='Diagnostiken':
                umstandRights=Diagnostik.getAll_fromKrankheit(Diagnostik,krankheit.get('Krankheit'), True)
                umstandAll=Diagnostik.getAll(Diagnostik)
            elif umstand=='Therapien':
                umstandRights=Therapie.getAll_fromKrankheit(Therapie,krankheit.get('Krankheit'), True)
                umstandAll=Therapie.getAll(Therapie)
            return umstandAll,umstandRights
        def fill_kh2umstand(krankheitendicts4fragen):
            """geht durch Dict und füllt fehlende Daten auf
            """
            for krankheit in krankheitendicts4fragen:
                for umstand in krankheit.get('Umstände'):
                    if krankheit.get('Umstände').get(umstand)==[]:
                        fill(krankheit,umstand)
        fill_kh2umstand(krankheitendicts4fragen)
    def kh2umstand_buildfragendicts_fromDatadicts(data4fragenDicts):
        """Baut aus den gegebenen Daten die Fragendicts auf
        Die Daten sind mit den Keys "Right" und "Wrong" gekennzeichnet
        """
        def buildFragetext4dict(krankheit, umstand, fragentyp):
            """Gibt Fragentext zurück
            für fragentyp 2 auch negativ gestellt
            """
            if fragentyp==2:
                nicht=' <u>nicht</u>'
            else:
                nicht=''
            if umstand == 'Ursachen':
                frage='Welche %s hat ein/e %s%s?'
            elif umstand == 'Symptome':
                frage='Welche %s treten bei einer/m %s%s auf?'
            elif umstand == 'Komplikationen':
                frage='Welche %s können bei einer/m %s%s auftreten?'
            elif umstand == 'Diagnostiken':
                frage='Welche %s nutzt man bei einer/m %s%s?'
            elif umstand == 'Therapien':
                frage='Welche %s nutzt man bei einer/m %s%s?'
            frage=frage%(umstand,krankheit,nicht)
            return frage
        def build(krankheit, umstand):
            """baut aus den Datendicts Dicts für die Fragen"""
            def set_rightans4fragen(antwortenDict, rightAnsAll, rnd):
                """füllt antwortenDict mit richtigen Antworten
                {antwort:right}
                """
                rightAns=[]
                while len(rightAns) < rnd: #füllt rightAns mit rnd richtigen antworten
                    rightAn=rightAnsAll[random.randint(0,len(rightAnsAll)-1)]
                    if rightAn not in rightAns:
                        rightAns.append(rightAn)
                        antwortenDict[rightAn]='right'
            def set_wrongans4fragen(antwortenDict, wrongAnsAll, rnd):
                """füllt antwortenDict mit falschen Antworten
                {antwort:wrong}
                """
                wrongAns=[]
                while len(wrongAns) < Frage.nAntworten-rnd:
                    wrongAn=wrongAnsAll[random.randint(0,len(wrongAnsAll)-1)]
                    if wrongAn not in wrongAns:
                        wrongAns.append(wrongAn)  
                        antwortenDict[wrongAn]='wrong' 
            antwortenDict={}
            antworten=krankheit.get('Umstände').get(umstand).get('Antworten')
            fragentyp = krankheit.get('Fragentyp')
            if 'Right' in antworten:
                rightAnsAll=antworten.get('Right')
                if Frage.nAntworten > len(rightAnsAll): # Falls weniger als 6 Elemente in Umstand sind
                    rnd=random.randint(1,len(rightAnsAll))
                else: 
                    rnd=random.randint(1,Frage.nAntworten-1)
                set_rightans4fragen(antwortenDict, rightAnsAll, rnd)
            if 'Wrong' in antworten:
                wrongAnsAll=antworten.get('Wrong')
                set_wrongans4fragen(antwortenDict, wrongAnsAll, rnd)
            if 'Right' in antworten or 'Wrong' in antworten: # Right or Wrong, da beim aktuallisieren nur das Element, dass aktualisiert wird
                                                                # Erneuert wird
                keys=list(antwortenDict.items())
                random.shuffle(keys)
                antwortenDict=dict(keys)
                krankheit.get('Umstände')[umstand]['Antworten']=antwortenDict
                krankheit.get('Umstände')[umstand]['Frage']=buildFragetext4dict(krankheit.get('Krankheit'), umstand, krankheit.get('Fragentyp'))
                krankheit.get('Umstände')[umstand]['Fragentitel']='Typ %s - %s (%s)'%(fragentyp, krankheit.get('Krankheit'), umstand)
        for krankheit in data4fragenDicts:
            for umstand in krankheit.get('Umstände'):
                build(krankheit, umstand)
        return data4fragenDicts

    def kh2umstand_initiatefragen(krankheiten4use):
        fragenDicts=Frage.kh2umstand_prepare_Dicts(krankheiten4use)
        Frage.kh2umstand_filldicts_withdata(fragenDicts)
        Frage.kh2umstand_buildfragendicts_fromDatadicts(fragenDicts)
        save_fragendicts2json(fragenDicts)
        return fragenDicts
    def kh2umstand_updatefrage(fragenDicts):
        Frage.kh2umstand_filldicts_withdata(fragenDicts, True)  
        Frage.kh2umstand_buildfragendicts_fromDatadicts(fragenDicts)  
        save_fragendicts2json(fragenDicts)
    
    def kh2umstand_prepare_fragen4xml(savedfragen):
        fragendicts=[]
        for krankheit in savedfragen:
            for fragedict in krankheit.get('Umstände').values():
                fragendicts.append(fragedict)
        return fragendicts

    def element2kh_get_fittingelements():
        elementcountermax=2
        krankheitendict=Krankheit.getall2dict()
        fittingelements=[]
        for krankheit in krankheitendict:
            for umstand in krankheit.get('Umstände'):
                for element in krankheit.get('Umstände').get(umstand):
                    elementcounter=0
                    elementkhs=[]
                    for _krankheit in krankheitendict:
                        for _element in _krankheit.get('Umstände').get(umstand):
                            if element ==_element:
                                elementcounter+=1
                                elementkhs.append(_krankheit.get('Krankheit'))
                    if elementcounter >=elementcountermax:
                        fittingelement={'Element':element, 'Umstand':umstand, 'Krankheiten':elementkhs}
                        if fittingelement not in fittingelements:
                            fittingelements.append(fittingelement)
        return fittingelements   
    def element2kh_getrandomfitting(fittingelements):
        rnd=random.randint(0,len(fittingelements)-1)
        return fittingelements[rnd]
    def element2kh_buildfragetext(element4frage):
        umstand=element4frage.get('Umstand')
        element=element4frage.get('Element')
        if umstand=='Ursachen':
            fragetext='Welche Krankheiten können aus der Ursache %s entstehen?'%(element)
        elif umstand=='Symptome':
            fragetext='Bei welchen Krankheiten tritt das Symptom %s auf?'%(element)
        elif umstand=='Komplikationen':
            fragetext='Bei welchen Krankheiten kommt es zu der Komplikation %s?'%(element)
        elif umstand=='Diagnostiken':
            fragetext='Bei welchen Krankheiten nutzt man das diagnostische Mittel %s?'%(element)
        elif umstand=='Therapien':
            fragetext='Bei welchen Krankheiten hilft die Therapie %s?'%(element)
        else:
            fragetext=''
        return fragetext
    def element2kh_pickantworten(element4frage):
        def element2kh_prepareantworten(element4frage):
            antworten=[]
            krankheitenwrong=Krankheit.getall()
            krankheitenright=element4frage.get('Krankheiten')
            for krankheit in krankheitenright:
                if krankheit in krankheitenwrong:
                    krankheitenwrong.remove(krankheit)
            for krankheitright in krankheitenright:
                antworten.append({krankheitright:'right'})
            for krankheitwrong in krankheitenwrong:
                antworten.append({krankheitwrong:'wrong'})
            return antworten
        antworten=element2kh_prepareantworten(element4frage)
        antworten4frage={}
        while len(antworten4frage) < Frage.nAntworten:
            rnd=random.randint(0,len(antworten)-1)
            rndantwort=antworten[rnd]
            antwortkeys=list(rndantwort.keys())
            antwortvalues=list(rndantwort.values())
            if antwortkeys[0] not in antworten4frage:
                antworten4frage[antwortkeys[0]]=antwortvalues[0]
        return antworten4frage
    def element2kh_build_frage(element):
        frage=Frage.element2kh_buildfragetext(element)
        antworten=Frage.element2kh_pickantworten(element)
        fragedict={'Frage':frage,'Antworten':antworten, 'Fragentitel':'Typ 3 - %s'%(element.get('Element'))}
        return fragedict
    def element2kh_initiatefragen(fragenanzahl):
        fragendicts=[]
        fittingelements=Frage.element2kh_get_fittingelements()
        f3fittingelements=len(fittingelements)
        elements4frage=[]
        for i in range(fragenanzahl):
            randelement=Frage.element2kh_getrandomfitting(fittingelements)
            if randelement not in elements4frage:
                elements4frage.append(randelement)
            else:
                i-=1
        for element in elements4frage:
            fragendicts.append(Frage.element2kh_build_frage(element))
        return fragendicts   
    def element2kh_updatefrage():
        fragedict=element2kh_build_frage()
        return fragedict

    def count_possibles():
        nKrankheiten = session.query(Krankheit.id).count()
        nUrsachen = session.query(Ursache.id).count()
        nSymptome = session.query(Symptom.id).count()
        nKomplikationen = session.query(Komplikation.id).count()
        nDiagnostiken = session.query(Diagnostik.id).count()
        nTherapien = session.query(Therapie.id).count()
        nElemente_f3 = len(Frage.element2kh_get_fittingelements())
        dict_nUmstände={'Ursachen':nUrsachen, 'Symptome':nSymptome, 'Komplikationen':nKomplikationen, 'Diagnostiken':nDiagnostiken, 'Therapien':nTherapien}
        
        krankheiten=Krankheit.getall()

        def count_elements_p_Krankheit_p_Umstand_2dict():
            counterdicts=[]
            krankheiten = Krankheit.getall2dict()
            for krankheit in krankheiten:
                counterdict={'Krankheit':krankheit.get('Krankheit'), 'Umstände':{}}
                umstandscounter={}
                for umstand in krankheit.get('Umstände'):
                    elements=krankheit.get('Umstände').get(umstand)
                    umstandscounter[umstand]=len(elements)
                counterdict['Umstände']=umstandscounter
                counterdicts.append(counterdict)
            return counterdicts
        
        def calc_possibles_pUmstand_f1_2(nUmstand, nUmstand_p_krankheit):
            nPossibles=math.comb(nUmstand, Frage.nAntworten)-math.comb(nUmstand-nUmstand_p_krankheit,Frage.nAntworten)
            return nPossibles
        
        def calc_possibles_f3():
            nPossibles_pf3=math.comb(nKrankheiten,Frage.nAntworten)
            nPossibles_f3=nPossibles_pf3*nElemente_f3
            return nPossibles_f3

        dict_nElements_pKrankheit_pUmstand = count_elements_p_Krankheit_p_Umstand_2dict()
        nPossibles_f1=0
        for krankheit in dict_nElements_pKrankheit_pUmstand:
            for umstand in krankheit.get('Umstände'):
                nUmstand=dict_nUmstände.get(umstand)
                elementcount=krankheit.get('Umstände').get(umstand)
                nPossibles_pUmstand=calc_possibles_pUmstand_f1_2(nUmstand, elementcount)
                nPossibles_f1+=nPossibles_pUmstand
                krankheit.get('Umstände')[umstand]=nPossibles_pUmstand

        nPossibles_f1_f2=nPossibles_f1*2
        nPossibles_f3=calc_possibles_f3()
        nPossibles=nPossibles_f1_f2+nPossibles_f3
        return nPossibles

def save_fragendicts2json(dicts):
    jsondict = json.dumps(dicts,ensure_ascii=False,)
    with open("fragen.json","w", encoding='utf-8') as fw:
        fw.write(jsondict)

def load_json2fragendicts():
    with open('fragen.json','r',encoding='utf-8') as fr:
        jsonstring=fr.read()
        dicts=json.loads(jsonstring)
    return dicts
    
def session_add_and_commit(new_obj_name):
    session.add(new_obj_name)
    session.commit()

def look4AlikesinDB():
    counter=0
    elements=session.query(Therapie).all()
    for elementx in elements:
        if elementx.name == None:
            continue
        for elementy in elements:
            if elementy.name == None:
                continue
            if elementy.name != elementx.name:
                charaufbauy=''
                for chary in elementy.name:
                    if charaufbauy in elementx.name:
                        charaufbauy=charaufbauy+chary
                    else:
                        if len(charaufbauy)>5 and 'Therapie' not in charaufbauy:
                            counter=counter+1
                            charaufbauy=''
                            print('Counter=%d\nElement 1: %s (%d)\nElement 2: %s (%d)\n'%(counter,elementx.name,elementx.id, elementy.name,elementy.id))

def getkhJoint(_class_name):
    '''
        _class.__name__ => ursachen, symptome, komplikationen, diagnostiken or therapien
        returns joint=session.query(Krankheit).join(Krankheit.umstände)
    '''
    if _class_name=='Ursache':
        joint=session.query(Krankheit).join(Krankheit.ursachen)
    elif _class_name=='Symptom':
        joint=session.query(Krankheit).join(Krankheit.symptome)
    elif _class_name=='Komplikation':
        joint=session.query(Krankheit).join(Krankheit.komplikationen)
    elif _class_name=='Diagnostik':
        joint=session.query(Krankheit).join(Krankheit.diagnostiken)
    elif _class_name=='Therapie':
        joint=session.query(Krankheit).join(Krankheit.therapien)
    else:
        joint=''
    return joint

def getkh_umstände(_class_name,krankheit):
    if _class_name=='Ursache':
        krankheit_umstand=krankheit.ursachen
    elif _class_name=='Symptom':
        krankheit_umstand=krankheit.symptome
    elif _class_name=='Komplikation':
        krankheit_umstand=krankheit.komplikationen
    elif _class_name=='Diagnostik':
        krankheit_umstand=krankheit.diagnostiken
    elif _class_name=='Therapie':
        krankheit_umstand=krankheit.therapien
    else:
        krankheit_umstand=''
    return krankheit_umstand

def setkh_Umstand_elemente(_class_name, krankheit,krankheit_elemente):
    '''
        _class.__name__ => ursachen, symptome, komplikationen, diagnostiken or therapien
        sets krankheit.umstände 2 krankheit_elemente
    '''
    if _class_name=='Ursache':
        krankheit.ursachen=krankheit_elemente
    elif _class_name=='Symptom':
        krankheit.symptome=krankheit_elemente
    elif _class_name=='Komplikation':
        krankheit.komplikationen=krankheit_elemente
    elif _class_name=='Diagnostik':
        krankheit.diagnostiken=krankheit_elemente
    elif _class_name=='Therapie':
        krankheit.therapien=krankheit_elemente

def element_getall():
    elemente=[]
    elemente+=Ursache.getAll(Ursache)
    elemente+=Symptom.getAll(Symptom)
    elemente+=Komplikation.getAll(Komplikation)
    elemente+=Diagnostik.getAll(Diagnostik)
    elemente+=Therapie.getAll(Therapie)
    return elemente

