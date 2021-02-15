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

roles_users = Table('roles_users',Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE")),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete="CASCADE"))
    )

class User(Base):
    __tablename__='users'

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(255))
    roles = relationship('Role', secondary=roles_users) 
    
    def regist(user_email, user_password):
        """Adds User to Database and gives the standard-role: 'User'
        Parameter: user_email = String
        Parameter: user_password = String
        """
        new_User=User(email=user_email, password=user_password)
        new_user_role=session.query(Role).filter(Role.name=='User').first()
        new_User.roles=[new_user_role]
        session_add_and_commit(new_User)

    def login(user_email, user_password):
        """returns True if Email exists and Password is right
        False if Email isnt existing or Password isnt right
        Parameter: user_email = String
        Parameter: user_password = String
        """
        login_bool=False
        users=session.query(User)
        for user in users:
            if user_email==user.email and user_password==user.password:
                login_bool=True
        return login_bool

    def getall2Dict():
        """ returns Userdata of all Users with roles in a list of Dictionarys
        Dict={'ID':user.id,'Email':user.email,'Password':user.password,'Roles':userrolelist}
        Return: userdicts = List (dict)
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
        """Deletes User with given user_ID
        Parameter: user_ID = String"""
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
        """Adds Role to Database
        Parameter: role_name = String, role_description = String
        """
        new_Role=Role(name=role_name, description=role_description)
        session_add_and_commit(new_Role)

    def role2User(user_email, role_name):
        """Adds Role with role_name to User with user_email
        Parameter: role_name = String, role_description = String
        """
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
        """Adds Krankheiten 2 db
        Parameter: krankheit_name = String"""
        new_Krankheit=Krankheit(name=krankheit_name)
        session_add_and_commit(new_Krankheit)

    def getall():
        """returns all Krankheiten
        return = sqlelements"""
        krankheiten=[]
        sqlelement=session.query(Krankheit).order_by(Krankheit.id.asc()).all()
        for row in sqlelement:
            krankheiten.append(row.name)
        return krankheiten

    def getall2dict():
        """returns Alle Krankheiten mit Umständen als Liste von Dicts
        return = List
        Dict : 
        [{
            'Krankheit':krankheit.name, 'Umstände':{
            "Ursachen":ursachen, "Symptome":symptome, "Komplikationen":komplikationen, "Diagnostiken":diagnostiken, "Therapien":therapien
        }}]"""
        krankheiten=session.query(Krankheit).all()
        krankheitendicts=[]
        for krankheit in krankheiten:
            krankheitdict={'Krankheit':krankheit.name, 'Umstände':{}}
            ursachen=Umstand.getAll_fromKrankheit(Ursache, krankheit.name, True)
            krankheitdict.get('Umstände')['Ursachen']=ursachen
            symptome=Umstand.getAll_fromKrankheit(Symptom, krankheit.name, True)
            krankheitdict.get('Umstände')['Symptome']=symptome
            komplikationen=Umstand.getAll_fromKrankheit(Komplikation, krankheit.name, True)
            krankheitdict.get('Umstände')['Komplikationen']=komplikationen
            diagnostiken=Umstand.getAll_fromKrankheit(Diagnostik, krankheit.name, True)
            krankheitdict.get('Umstände')['Diagnostiken']=diagnostiken
            therapien=Umstand.getAll_fromKrankheit(Therapie, krankheit.name, True)
            krankheitdict.get('Umstände')['Therapien']=therapien
            krankheitendicts.append(krankheitdict)
        return krankheitendicts  

    def change(krankheit_name, new_name):
        """ Ändert Name der Krankheit
        Parameter: krankheit_name = String
        Parameter: new_name = String
        
        krankheit_name = alter Name der Krankheit
        new_name = neuer Name für Krankheit
        """
        element2change=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
        element2change.name=new_name
        session_add_and_commit(element2change)       
    
    def delete(krankheit_name):
        """löscht Krankheit mit dem Namen: krankheit_name
        Parameter: krankheit_name
        """
        element2delete=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
        session.delete(element2delete)
        session.commit()

    def countelements():
        """zählt Krankheiten
        return: nKrankheiten = int
        """
        nKrankheiten = session.query(Krankheit.id).count()
        return nKrankheiten

class Umstand(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

    def add(_class, krankheit_name, element_name):
        """fügt Element mit element_name in Krankheit mit krankheit_name in den Umstand _class ein 
        Parameter: _class = Klasse (Umstand), krankheit_name = String, element_name = String
        """
        if issubclass(_class, Umstand):
            element=session.query(_class).filter(_class.name==element_name).first() 
            if element is None:
                element=_class(name=element_name) 
                session_add_and_commit(element)
            krankheit_elemente=_class.getAll_fromKrankheit(_class, krankheit_name, False) 
            krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first() 
            krankheit_elemente.append(element) 
            setkh_Umstand_elemente(_class.__name__, krankheit, krankheit_elemente)
            session.commit()
        else:
            pass # Fehlermeldung

    def getAll(_class):
        """returns Alle Elemente des Umstands _class
        Parameter: _class = Klasse (Umstand)
        Return: elemente = List[sqlelement]
        """
        if issubclass(_class, Umstand):
            elemente=[]
            elementesql=session.query(_class).all()
            for element in elementesql:
                if element.name==None: # => element = Krankheit
                    element=session.query(Krankheit).filter(Krankheit.id==element.krankheit_id).first() 
                elemente.append(element.name) 
            return elemente
        else:
            pass # Fehlermeldung

    def getAll_fromKrankheit(_class, krankheit_name, toString=False):
        ''' returns Elemente des Umstands _class der Krankheit krankheit_name
        Parameter: _class = Klasse (Umstand), krankheit_name = String, toString = Boolean
            toString = True => returns Namestrings
            toString = False => returns sqlelements 
        Return: krankheit_elemente = List[String]
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
        """Ändert den Namen eines Elements
        Parameter: _class = Klasse (Umstand), element_name = String, newElement_name = String
        """
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
        Parameter: _class = Klasse (Umstand), krankheit_name = String, element_name = String, newElement_name = String
        """
        if issubclass(_class, Umstand):
            _classquery=session.query(_class)
            kh_query=session.query(Krankheit)
            element=_classquery.filter(_class.name==element_name).first()
            krankheit_elemente=_class.getAll_fromKrankheit(_class, krankheit_name, False)
            krankheit_old=kh_query.filter(Krankheit.name==element_name).first()
            if element is None: #None => element=Krankheit
                element=_classquery.filter(_class.krankheit_id==krankheit_old.id).first()
            krankheit_elemente.remove(element)
            krankheit=kh_query.filter(Krankheit.name==krankheit_name).first()
            new_kh_element=kh_query.filter(Krankheit.name==newElement_name).first()
            if new_kh_element is None:
                new_element=_classquery.filter(_class.name==newElement_name).first()
                if new_element is None:
                    new_element=_class(name=newElement_name)
            else:
                new_element=new_kh_element       
            krankheit_elemente.append(new_element)
            setkh_Umstand_elemente(_class.__name__, krankheit, krankheit_elemente)
            session.commit()
        else:
            pass # Fehlermeldung

    def deleteall(_class, element_name):
        """lösche Element element_name des Umstands _class aus DB
        Parameter: _class = Klasse (Umstand), element_name = String
        """
        if issubclass(_class, Umstand):
            element2delete=session.query(_class).filter(_class.name==element_name).first()
            if element2delete is None: #=> element2delete=Krankheit
                element2delete=session.query(Krankheit).filter(Krankheit.name==element_name).first()   
            session.delete(element2delete)
            session.commit()
        else:
            pass # Fehlermeldung

    def deleteone(_class, krankheit_name, element2del_name):
        """Entferne Element element2del_name aus Krankheit krankheit_name des Umstand _class
        Parameter: _class = Klasse (Umstand), krankheit_name = String, element2del_name = String
        """
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
        """ Sucht nach Element element2look4 und gibt Dict mit verbundenen Umstand und Krankheiten aus 
        Parameter: element2look4 = String
        return: foundkrankheitendict = Dict
        Dict={'Foundelement':'element2look4', 'Hideouts':[{'Krankheit':krankheit,'Umstand':umstand}]}
        """
        krankheitendicts=Krankheit.getall2dict()
        foundkrankheitendict={'Foundelement':'', 'Hideouts':[]}
        for krankheitdict in krankheitendicts:
            for umstand in krankheitdict.get('Umstände'):
                for element in krankheitdict.get('Umstände').get(umstand):
                    if element.lower()==element2look4.lower():
                        foundelement=element
                        foundkrankheitendict['Foundelement']=foundelement
                        hideout={'Krankheit':krankheitdict.get('Krankheit'),'Umstand':umstand}
                        foundkrankheitendict.get('Hideouts').append(hideout)         
        if foundkrankheitendict.get('Foundelement')=='':
            foundkrankheitendict['Foundelement']=element2look4
        return foundkrankheitendict

    def countelements(_class):
        """zählt Elemente des Umstands _class
        Parameter: _class = Klasse (Umstand)
        return: nUmstand = int
        """
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
        """fügt eine Krankheit hinzu zu Umstand (Ursache & Komplikation) hinzu
        Parameter: _class = Klasse (VerknüpfenderUmstand), krankheit_name = String, krankheit2add = String
        """
        if issubclass(_class, VerknüpfenderUmstand):
            if krankheit_name!=krankheit2add:
                kh_query=session.query(Krankheit)
                krankheit=kh_query.filter(Krankheit.name==krankheit2add).first()
                element_kh=session.query(_class).filter(_class.krankheit_id==krankheit.id).first()
                if element_kh is None: 
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
        """prepariert Dicts für ausgewählte Krankheiten krankheiten4use und jeweilige Umstände (nUmstände=5)
            Fragentyp 1 und 2
        => pro Krankheit 10 Dicts
        Parameter: krankheiten4use = List [Strings]
        Return: krankheitenfragendicts = List [Dict]
            Dict = {'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
                    'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}
        """
        def prepare_kh2umstand(fragentyp):
            """baut die Dictionarys auf
            Parameter: fragentyp = int (1 or 2) 
            Return = krankheitenfragendict = Dict
            {'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
            'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}
            """
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
        Parameter: 
            krankheitendicts4fragen = List [Dict], update = Boolean
                Dict = {'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
                    'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}
                update=False => Alle Daten werden neu generiert
                update=True => Nur Fehlende Daten werden neu generiert
        """
        def fill_umstand_with_elements(krankheitdict,umstand):
            """Fügt im Dict krankheitdict den umstand d. krankheit mit richtigen und falschen Elementen
            Parameter: krankheitdict = Dict, umstand = String
            Dict={'Frage':'','Antworten':{'Right':[],'Wrong':[]}}
            """
            krankheitdict.get('Umstände')[umstand]={'Frage':'','Antworten':{'Right':[],'Wrong':[]}}
            (umstandAll, umstandRights)=decide_umstand(krankheitdict,umstand)
            for element in umstandRights:
                krankheitdict.get('Umstände')[umstand]['Antworten']['Right'].append(element)
                if element in umstandAll:
                    umstandAll.remove(element)
            umstandWrongs=umstandAll
            for element in umstandWrongs:
                krankheitdict.get('Umstände')[umstand]['Antworten']['Wrong'].append(element)           
        def decide_umstand(krankheitdict,umstand):
            """gibt je nach Krankheit und Umstand die richtigen und falschen Antworten zurück
            Parameter: krankheitdict = Dict, umstand = String
            Return: umstandAll = List, umstandRights = List
            """
            if umstand=='Ursachen':
                umstandRights=Ursache.getAll_fromKrankheit(Ursache,krankheitdict.get('Krankheit'), True)
                umstandAll=Ursache.getAll(Ursache)
            elif umstand=='Symptome':
                umstandRights=Symptom.getAll_fromKrankheit(Symptom,krankheitdict.get('Krankheit'), True)
                umstandAll=Symptom.getAll(Symptom)
            elif umstand=='Komplikationen':
                umstandRights=Komplikation.getAll_fromKrankheit(Komplikation,krankheitdict.get('Krankheit'), True)
                umstandAll=Komplikation.getAll(Komplikation)
            elif umstand=='Diagnostiken':
                umstandRights=Diagnostik.getAll_fromKrankheit(Diagnostik,krankheitdict.get('Krankheit'), True)
                umstandAll=Diagnostik.getAll(Diagnostik)
            elif umstand=='Therapien':
                umstandRights=Therapie.getAll_fromKrankheit(Therapie,krankheitdict.get('Krankheit'), True)
                umstandAll=Therapie.getAll(Therapie)
            return umstandAll,umstandRights
        def fill_kh_dicts_with_umstandelements(krankheitendicts4fragen):
            """geht durch Dict und füllt fehlende Daten auf
            Parameter krankheitendicts4fragen = List[Dict]
            Dict = {'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
                    'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}
            """
            for krankheitdict in krankheitendicts4fragen:
                for umstand in krankheitdict.get('Umstände'):
                    if krankheitdict.get('Umstände').get(umstand)==[]:
                        fill_umstand_with_elements(krankheitdict,umstand)
        fill_kh_dicts_with_umstandelements(krankheitendicts4fragen)
    def kh2umstand_buildfragendicts_fromDatadicts(data4fragenDicts):
        """Baut aus den gegebenen Daten die Fragendicts auf
        Die Daten sind mit den Keys "Right" und "Wrong" gekennzeichnet
        
        Parameter: data4fragenDicts = List[Dict]
        Dict = {'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
                    'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}
        """
        def buildFragetext4dict(krankheit, umstand, fragentyp):
            """Gibt Fragentext zurück
            für fragentyp 2 auch negativ gestellt
            Parameter: krankheit = String, umstand = string, fragentyp = int (1 or 2)
            Return: frage = String
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
        def build_fragedict(krankheitdict, umstand):
            """baut aus den Datendicts Dicts für die Fragen
            Parameter: krankheit = Dict, umstand = String
            """
            def fill_dict_with_ans_E_kh(antwortenDict, rightAnsAll, rnd, fragentyp):
                """füllt antwortenDict mit Antworten E Krankheit  
                Parameter: antwortenDict = Dict, rightAnsAll = List, rnd = int, fragentyp = int (1 or 2)
                fragentyp 1 Antwort E Krankheit = 'right'
                fragentyp 2 Antwort E Krankheit = 'wrong'
                """
                rightAns=[]
                while len(rightAns) < rnd:
                    rightAn=rightAnsAll[random.randint(0,len(rightAnsAll)-1)]
                    if rightAn not in rightAns: 
                        rightAns.append(rightAn)
                        if fragentyp==1:
                            antwortenDict[rightAn]='right'
                        elif fragentyp==2:
                            antwortenDict[rightAn]='wrong'
            def fill_dict_with_ans_nE_kh(antwortenDict, wrongAnsAll, rnd, fragentyp):
                """füllt antwortenDict mit Antworten !E Krankheit  
                Parameter: antwortenDict = Dict, wrongAnsAll = List, rnd = int, fragentyp = int (1 or 2)
                fragentyp 1 Antwort !E Krankheit = 'wrong'
                fragentyp 2 Antwort !E Krankheit = 'right'
                """
                wrongAns=[]
                while len(wrongAns) < Frage.nAntworten-rnd:
                    wrongAn=wrongAnsAll[random.randint(0,len(wrongAnsAll)-1)]
                    if wrongAn not in wrongAns:
                        wrongAns.append(wrongAn) 
                        if fragentyp==1:
                            antwortenDict[wrongAn]='wrong'
                        elif fragentyp==2:
                            antwortenDict[wrongAn]='right'
            def rnd_n_ans_E_kh(fragentyp, rightAnsAll):
                """returns rnd Nummer für Anzahl antworten E kh
                Parameter: fragentyp = int (1 or 2), rightAnsAll = List
                Return: rnd = int
                """
                if fragentyp==1:
                    if Frage.nAntworten > len(rightAnsAll): 
                        rnd=random.randint(1,len(rightAnsAll)) 
                    else: 
                        rnd=random.randint(1,Frage.nAntworten)
                elif fragentyp==2:
                    if Frage.nAntworten > len(rightAnsAll):
                        rnd=random.randint(0,len(rightAnsAll))
                    else: 
                        rnd=random.randint(0,Frage.nAntworten-1)
                return rnd
            def fill_fragedict(antwortenDict,fragentyp,krankheitdict,umstand):
                """baut aus Parametern fragendict
                Parameter: antwortenDict = Dict, fragentyp = int (1 or 2), krankheitdict = Dict, umstand = String
                antwortenDict = {element1:'right', element2:'wrong',...}
                krankheitdict = {'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
                                'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}
                """
                keys=list(antwortenDict.items()) # Alle fürs shufflen in Liste
                random.shuffle(keys)    #Liste shuffeln
                antwortenDict=dict(keys)    #Liste wieder in Dict
                krankheitdict.get('Umstände')[umstand]['Fragentitel']='Typ %s - %s (%s)'%(fragentyp, krankheitdict.get('Krankheit'), umstand)
                krankheitdict.get('Umstände')[umstand]['Frage']=buildFragetext4dict(krankheitdict.get('Krankheit'), umstand, fragentyp)
                krankheitdict.get('Umstände')[umstand]['Antworten']=antwortenDict
                
            antwortenDict={}
            antworten=krankheitdict.get('Umstände').get(umstand).get('Antworten')
            fragentyp = krankheitdict.get('Fragentyp')
            if 'Right' in antworten:
                rightAnsAll=antworten.get('Right')
                rnd=rnd_n_ans_E_kh(fragentyp, rightAnsAll)
                fill_dict_with_ans_E_kh(antwortenDict, rightAnsAll, rnd, fragentyp)
            if 'Wrong' in antworten:
                wrongAnsAll=antworten.get('Wrong')
                fill_dict_with_ans_nE_kh(antwortenDict, wrongAnsAll, rnd, fragentyp)
            if 'Right' in antworten or 'Wrong' in antworten: # Right or Wrong, da beim aktuallisieren nur das Element, dass aktualisiert wird Erneuert wird
                fill_fragedict(antwortenDict, fragentyp, krankheitdict, umstand)
        for krankheitdict in data4fragenDicts:
            for umstand in krankheitdict.get('Umstände'):
                build_fragedict(krankheitdict, umstand)

    def kh2umstand_initiatefragen(krankheiten4use):
        """Kompletter Aufbau der Fragen pro Krankheit in krankheiten4use (5 Fragen pro Krankheit pro Fragentyp)
        Parameter: krankheiten4use = List[krankheiten]
        """
        fragenDicts=Frage.kh2umstand_prepare_Dicts(krankheiten4use)
        Frage.kh2umstand_filldicts_withdata(fragenDicts)
        Frage.kh2umstand_buildfragendicts_fromDatadicts(fragenDicts)
        save_fragendicts2json(fragenDicts)
        return fragenDicts
    def kh2umstand_updatefrage(fragenDicts):
        """generiere entfernte Fragen neu
        Parameter: fragenDicts = List[Dict]
        Dict = {'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
                'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}
        """
        Frage.kh2umstand_filldicts_withdata(fragenDicts, True)  
        Frage.kh2umstand_buildfragendicts_fromDatadicts(fragenDicts)  
        save_fragendicts2json(fragenDicts)
    
    def kh2umstand_prepare_fragen4xml(fragenDicts):
        """Entfernt den Key Umstände -> Einheitliches Dict für jede Frage
        egal ob typ1, typ2 oder typ3
        Parameter: fragenDicts = List[Dict]
        Dict = {'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
                'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}
        """
        fragendicts=[]
        for krankheitdict in fragenDicts:
            for fragedict in krankheitdict.get('Umstände').values():
                fragendicts.append(fragedict)
        return fragendicts

    def element2kh_get_fittingelementsdicts():
        """Holt die für die Frageart 3 geeigneten Elemente aus Datenbank
        -> Element in Mindestens 2 Krankheiten enthalten
        Return fittingelementsdicts = List[Dict]
            Dict: fittingelementdict={'Element':element, 'Umstand':umstand, 'Krankheiten':elementkhs}
        """
        elementcountermax=2 #min in 2 Krankheiten
        krankheitendicts=Krankheit.getall2dict()
        fittingelementsdicts=[]
        for krankheitdict in krankheitendicts:
            for umstand in krankheitdict.get('Umstände'): 
                for element in krankheitdict.get('Umstände').get(umstand):
                    elementcounter=0 # zählt Elemente, die in mehreren Krankheiten vorkommen
                    elementkhs=[]
                    for _krankheitdict in krankheitendicts:
                        for _element in _krankheitdict.get('Umstände').get(umstand):
                            if element ==_element:
                                elementcounter+=1
                                elementkhs.append(_krankheitdict.get('Krankheit'))
                    if elementcounter >=elementcountermax: 
                        fittingelementdict={'Element':element, 'Umstand':umstand, 'Krankheiten':elementkhs}
                        if fittingelementdict not in fittingelementsdicts: # gegen doppelte
                            fittingelementsdicts.append(fittingelementdict)
        return fittingelementsdicts   
    def element2kh_getrandomfitting(fittingelementsdicts):
        """gibt ein Zufällig ausgewähltes Element aus den Passenden Elementen für Frageart3 aus
        Parameter fittingelementsdicts = List[Dict]
        Return fittingelementsdicts[rnd] = Dict
            Dict: fittingelementdict={'Element':element, 'Umstand':umstand, 'Krankheiten':elementkhs}
        """
        rnd=random.randint(0,len(fittingelementsdicts)-1)
        return fittingelementsdicts[rnd]
    def element2kh_buildfragetext(element4frage_dict):
        """Fragetext für Frageart3
        Parameter: element4frage_dict = Dict
            Dict = {'Element':element, 'Umstand':umstand, 'Krankheiten':elementkhs}
        Return: fragetext = String
        """
        umstand=element4frage_dict.get('Umstand')
        element=element4frage_dict.get('Element')
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
    def element2kh_pickantworten(element4frage_dict):
        """füllt Frage mit n randomisierten Antwortmöglichkeiten
        n = nAntworten = 6
        Parameter: element4frage_dict = Dict
            Dict = {'Element':element, 'Umstand':umstand, 'Krankheiten':elementkhs}
        Return: antworten4frage = Dict => {Element1 : 'wrong', Element2:'right',...}
        """
        def element2kh_prepareantworten(element4frage_dict):
            """holt alle Krankheiten und sortiert sie nach richtig und falsch
            mit Bezug auf Element der Frage
            Parameter: element4frage_dict = Dict
                Dict = {'Element':element, 'Umstand':umstand, 'Krankheiten':elementkhs} 
            Return antworten = List[Dict]
                Dict = {Element1 : 'wrong', Element2:'right',...}
            """
            antworten=[]
            krankheitenwrong=Krankheit.getall()
            krankheitenright=element4frage_dict.get('Krankheiten')
            for krankheit in krankheitenright:
                if krankheit in krankheitenwrong:
                    krankheitenwrong.remove(krankheit) 
            for krankheitright in krankheitenright:
                antworten.append({krankheitright:'right'})
            for krankheitwrong in krankheitenwrong:
                antworten.append({krankheitwrong:'wrong'})
            return antworten
        antworten=element2kh_prepareantworten(element4frage_dict)
        antworten4frage={}
        while len(antworten4frage) < Frage.nAntworten:
            rnd=random.randint(0,len(antworten)-1)
            rndantwort=antworten[rnd] 
            antwortkeys=list(rndantwort.keys()) 
            antwortvalues=list(rndantwort.values()) 
            if antwortkeys[0] not in antworten4frage: 
                antworten4frage[antwortkeys[0]]=antwortvalues[0] 
        return antworten4frage
    def element2kh_build_frage(element_dict):
        """baut eine Frage des Fragentyp3 mit Element element_dict
        Parameter: element_dict = Dict
            Dict: element_dict = {'Element':element, 'Umstand':umstand, 'Krankheiten':elementkhs}
        Return: fragedict = Dict => {'Frage':frage,'Antworten':antworten, 'Fragentitel':'Typ 3 - Element'}
        """
        frage=Frage.element2kh_buildfragetext(element_dict)
        antworten=Frage.element2kh_pickantworten(element_dict)
        fragedict={'Frage':frage,'Antworten':antworten, 'Fragentitel':'Typ 3 - %s'%(element_dict.get('Element'))}
        return fragedict
    def element2kh_initiatefragen(fragenanzahl):
        """Baut aus zufällig ausgewählten Elementen n Fragen
        n=fragenanzahl
        Parameter fragenanzahl = int
        Return fragendicts = List[fragedict]
            fragedict = Dict => {'Frage':frage,'Antworten':antworten, 'Fragentitel':'Typ 3 - Element'}
        """
        fragendicts=[]
        fittingelementsdicts=Frage.element2kh_get_fittingelementsdicts()
        elements4frage_dicts=[]
        for i in range(fragenanzahl):
            randelement=Frage.element2kh_getrandomfitting(fittingelementsdicts)
            if randelement not in elements4frage_dicts:
                elements4frage_dicts.append(randelement) 
            else:
                i-=1
        for element_dict in elements4frage_dicts:
            fragendicts.append(Frage.element2kh_build_frage(element_dict))
        return fragendicts   
    def element2kh_updatefrage():
        """noch nicht implementiert"""
        fragedict=element2kh_build_frage()
        return fragedict

    def count_possibles():
        """Zählt mögliche Fragen für Typ1,2,3
        Return nPossibles = int => Anzahl aller möglichen Fragen"""
        nKrankheiten = session.query(Krankheit.id).count()
        nUrsachen = session.query(Ursache.id).count()
        nSymptome = session.query(Symptom.id).count()
        nKomplikationen = session.query(Komplikation.id).count()
        nDiagnostiken = session.query(Diagnostik.id).count()
        nTherapien = session.query(Therapie.id).count()
        nElemente_f3 = len(Frage.element2kh_get_fittingelementsdicts())
        dict_nUmstände={'Ursachen':nUrsachen, 'Symptome':nSymptome, 'Komplikationen':nKomplikationen, 'Diagnostiken':nDiagnostiken, 'Therapien':nTherapien}
        
        krankheiten=Krankheit.getall()

        def count_elements_p_Krankheit_p_Umstand_2dict():
            """Zählt alle Umstände pro Krankheit und gibt sie separat in Dict aus
            counterdicts = List[Dict]
                Dict = {'Krankheit':krankheit.get('Krankheit'), 'Umstände':{"Symptome":Anzahl,...}}"""
            counterdicts=[]
            krankheitendicts = Krankheit.getall2dict()
            for krankheitdict in krankheitendicts:
                counterdict={'Krankheit':krankheitdict.get('Krankheit'), 'Umstände':{}}
                umstandscounter={}
                for umstand in krankheitdict.get('Umstände'):
                    elements=krankheitdict.get('Umstände').get(umstand)
                    umstandscounter[umstand]=len(elements)
                counterdict['Umstände']=umstandscounter
                counterdicts.append(counterdict)
            return counterdicts
        
        def calc_possibles_pUmstand_f1_2(nUmstand, nUmstand_p_krankheit):
            """Berechnet Anzahl an möglichen Fragen pro Krankheit und pro Umstand für Typ 1
            Parameter: nUmstand = int => Anzahl Umstandselemente gesamt, nUmstand_p_krankheit = int => Anzahl Umstandselement E Krankheit
            return nPossibles = int => mögliche Anzahl Fragen
            """
            nPossibles=math.comb(nUmstand, Frage.nAntworten)-math.comb(nUmstand-nUmstand_p_krankheit,Frage.nAntworten)
            return nPossibles
        
        def calc_possibles_f3():
            """Berechnet Anzahl möglicher Fragen für Typ3
            Return nPossibles_f3 = int => Anzahl möglicher Fragen
            """
            nPossibles_pf3=math.comb(nKrankheiten,Frage.nAntworten)
            nPossibles_f3=nPossibles_pf3*nElemente_f3
            return nPossibles_f3

        dict_nElements_pKrankheit_pUmstand = count_elements_p_Krankheit_p_Umstand_2dict()
        nPossibles_f1=0
        for krankheitdict in dict_nElements_pKrankheit_pUmstand:
            for umstand in krankheitdict.get('Umstände'):
                nUmstand=dict_nUmstände.get(umstand)
                elementcount=krankheitdict.get('Umstände').get(umstand)
                nPossibles_pUmstand=calc_possibles_pUmstand_f1_2(nUmstand, elementcount)
                nPossibles_f1+=nPossibles_pUmstand
                krankheitdict.get('Umstände')[umstand]=nPossibles_pUmstand

        nPossibles_f1_f2=nPossibles_f1*2
        nPossibles_f3=calc_possibles_f3()
        nPossibles=nPossibles_f1_f2+nPossibles_f3
        return nPossibles

def save_fragendicts2json(fragendicts):
    """Speichert fragendicts in Json
    Parameter: fragendicts = List[Dict]
        Dict = {'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
                'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}
    """
    jsondict = json.dumps(fragendicts,ensure_ascii=False,)
    with open("fragen.json","w", encoding='utf-8') as fw:
        fw.write(jsondict)

def load_json2fragendicts():
    """Läd fragendicts von aus json-file
    Return: fragendicts = List[Dict]
        Dict = {'Krankheit':krankheit, 'Umstände':{'Ursachen':[],'Symptome':[],
                'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]},'Fragentyp':fragentyp}
    """
    with open('fragen.json','r',encoding='utf-8') as fr:
        jsonstring=fr.read()
        fragendicts=json.loads(jsonstring)
    return fragendicts
    
def session_add_and_commit(new_obj_name):
    """speichert new_obj_name in Datenbank ein
    Parameter: new_obj_name = sqlelement
    """
    session.add(new_obj_name)
    session.commit()

def look4AlikesinDB():
    """Nicht implementiert!
    schaut nach Elementen, die ähnlich aussehen
    gg Elementsynonyme
    """
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
        Umstand String => SQLelemente 
        Parameter: _class_name = String => ursachen, symptome, komplikationen, diagnostiken or therapien
        Return: joint = List[sqlelement] 
            joint=session.query(Krankheit).join(Krankheit.umstände)
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
    """gibt Umstandselemente in Verbindung mit Krankheit zurück
    Parameter: krankheit = sqlelement, _class_name = String(Ursache, Symptom, Komplikation, Diagnostik, Therapie)
    Return: krankheit_umstand = sqlelement => krankheit.umstände
    """
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
    ''' fügt krankheit_elemente zu krankheit.umstand hinzu => umstand=_class_name
        Parameter: _class_name = String => Ursache, Symptom, Komplikation, Diagnostik or Therapie
                krankheit = sqlelement
                krankheit_elemente = List[sqlelement]
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
    """gibt alle Umstände mit Elementen aus jeder Krankheit aus
        Return: elemente = List[sqlelement]
    """
    elemente=[]
    elemente+=Ursache.getAll(Ursache)
    elemente+=Symptom.getAll(Symptom)
    elemente+=Komplikation.getAll(Komplikation)
    elemente+=Diagnostik.getAll(Diagnostik)
    elemente+=Therapie.getAll(Therapie)
    return elemente

