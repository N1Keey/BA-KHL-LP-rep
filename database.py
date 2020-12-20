from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Table, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from pprint import pprint

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
        ID, Email, Password, Roles are the Keys
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
        """Get all Krankheiten"""
        krankheiten=[]
        sqlelement=session.query(Krankheit).order_by(Krankheit.id.asc()).all()
        for row in sqlelement:
            krankheiten.append(row.name)
        return krankheiten

    def getall2dict():
        krankheiten=session.query(Krankheit).all()
        krankheitendicts=[]
        for krankheit in krankheiten:
            krankheitendict={'Krankheit':krankheit.name}
            ursachen=[]
            for ursache in krankheit.ursachen:
                if ursache.name is None:
                    ursache=session.query(Krankheit).filter(Krankheit.id==ursache.krankheit_id).first()
                ursachen.append(ursache.name)
            krankheitendict['Ursachen']=ursachen
            symptome=[]
            for symptom in krankheit.symptome:
                symptome.append(symptom.name)
            krankheitendict['Symptom']=symptome
            komplikationen=[]
            for komplikation in krankheit.komplikationen:
                if komplikation.name is None:
                        komplikation=session.query(Krankheit).filter(Krankheit.id==komplikation.krankheit_id).first()
                komplikationen.append(komplikation.name)
            krankheitendict['Komplikation']=komplikationen
            diagnostiken=[]
            for diagnostik in krankheit.diagnostiken:
                diagnostiken.append(diagnostik.name)
            krankheitendict['Diagnostiken']=diagnostiken
            therapien=[]
            for therapie in krankheit.therapien:
                therapien.append(therapie.name)
            krankheitendict['Therapien']=therapien
            krankheitendicts.append(krankheitendict)
        return krankheitendicts  

class Umstand(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

    __mapper_args__ = {
    'polymorphic_identity':'umstand',
    'polymorphic_on':type
    }
    
    @classmethod
    def get_classname(cls):
        return cls.__name__

    def queryfromclass():
        '''returns krankheit, umstand, krankheit2umstand'''
        query_krankheit=session.query(Krankheit)
        classname=getclassname()
        if classname=='Ursache':
            query_umstand=session.query(Ursache)
            query_krankheit2umstand=query_krankheit.join(Krankheit.ursachen)
        elif classname=='Symptom':
            query_umstand=session.query(Symptom)
            query_krankheit2umstand=query_krankheit.join(Krankheit.symptome)
        elif classname=='Komplikation':
            query_umstand=session.query(Komplikation)
            query_krankheit2umstand=query_krankheit.join(Krankheit.komplikationen)
        elif classname=='Diagnostik':
            query_umstand=session.query(Diagnostik)
            query_krankheit2umstand=query_krankheit.join(Krankheit.diagnostiken)
        elif classname=='Therapie':
            query_umstand=session.query(Therapie)
            query_krankheit2umstand=query_krankheit.join(Krankheit.therapien)
        else:
            query_umstand='not found'
            query_krankheit2umstand='not found'
        return query_krankheit, query_umstand, query_krankheit2umstand

    def link_Content2krankheit(krankheit, content):
        if classname=='Ursache':
            krankheit.ursachen=content
        elif classname=='Symptom':
            krankheit.symptome=content
        elif classname=='Komplikation':
            krankheit.komplikationen=content
        elif classname=='Diagnostik':
            krankheit.diagnostiken=content
        elif classname=='Therapie':
            krankheit.therapien=content
        session.commit()

    def get_contentfromkrankheit(krankheit):
        if classname=='Ursache':
            krankheit_dot_umstand=krankheit.ursachen
        elif classname=='Symptom':
            krankheit_dot_umstand=krankheit.symptome
        elif classname=='Komplikation':
            krankheit_dot_umstand=krankheit.komplikationen
        elif classname=='Diagnostik':
            krankheit_dot_umstand=krankheit.diagnostiken
        elif classname=='Therapie':
            krankheit_dot_umstand=krankheit.therapien
        return krankheit_dot_umstand

    def new_Object(object_name):
        if classname=='Ursache':
            new_element=Ursache(name=object_name)
        elif classname=='Symptom':
            new_element=Symptom(name=object_name)
        elif classname=='Komplikation':
            new_element=Komplikation(name=object_name)
        elif classname=='Diagnostik':
            new_element=Diagnostik(name=object_name)
        elif classname=='Therapie':
            new_element=Therapie(name=object_name)
        return new_element

    def getelems_from_krankheit2umstand(krankheit):
        krankheit_umstand=[]
        krankheit_dot_umstand=Umstand.get_contentfromkrankheit(krankheit)
        for elem in krankheit_dot_umstand:
            krankheit_umstand.append(elem)
        return krankheit_umstand  

    def add(krankheit_name, element_name):
        query_krankheit,query_umstand,query_krankheit2umstand=Umstand.queryclass()
        query_element=query_umstand.filter(text('name=%s'%(element_name))).first() #query1 schemaelement
        content=Umstand.getAll_fromKrankheit(krankheit_name, False) #3 get all schemaelements von kh
        if query_element is None:
            new_element=Umstand.new_Object(element_name) #2 anlegen von schemaelement fals noch nicht vorhanden
            session_add_and_commit(new_element)
            content.append(new_element)
        else:
            content.append(query_element)
        krankheit=query_krankheit.filter(Krankheit.name==krankheit_name).first() #4 query krankheit
        Umstand.link_Content2krankheit(krankheit,content)

    def getAll_fromKrankheit(krankheit_name, toString=False):
        query_krankheit,query_umstand,query_krankheit2umstand=Umstand.queryfromclass()
        krankheit_umstand=[]
        try:
            krankheit=query_krankheit2umstand.filter(Krankheit.name==krankheit_name).first()
            krankheit_umstand=Umstand.getelems_from_krankheit2umstand(krankheit)
            if toString==True:
                umstandstrings=[]
                for elem in krankheit_umstand:
                    if elem.name is None:
                        umstand=query_krankheit.filter(Krankheit.id==elem.krankheit_id).first()
                    umstandstrings.append(umstand.name)
                krankheit_umstand=umstandstrings
        except AttributeError:
            krankheit_umstand=[]
        return krankheit_umstand

    def getAll():
        query_krankheit,query_umstand,query_krankheit2umstand=Umstand.queryclass()
        elemente=[]
        elementesql=query_umstand.all()
        for element in elementesql:
            elemente.append(element.name)
        return elemente

class VerknüpfenderUmstand(Umstand):
    __abstract__ = True
    krankheit_id = Column(Integer, unique=True)

    __mapper_args__ = {
    'polymorphic_identity':'umstanduok',
    'polymorphic_on':type
    }
    def queryfromclass():
        super(VerknüpfenderUmstand).queryfromclass()
    def link_Content2krankheit(krankheit, content):
        super(VerknüpfenderUmstand).link_Content2krankheit(krankheit, content)
    def get_contentfromkrankheit(krankheit):
        super(VerknüpfenderUmstand).get_contentfromkrankheit(krankheit)
    def new_Object(object_name):
        super(VerknüpfenderUmstand).new_Object(object_name)
    def getelems_from_krankheit2umstand(krankheit):
        super(VerknüpfenderUmstand).getelems_from_krankheit2umstand(krankheit)
    def add(krankheit_name, element_name):
        super(VerknüpfenderUmstand).add(krankheit_name, element_name)
    def getAll_fromKrankheit(krankheit_name, toString=False):
        super(VerknüpfenderUmstand).getAll_fromKrankheit(krankheit_name, toString=False)
    def getAll():
        super(VerknüpfenderUmstand).getAll()

class Ursache(VerknüpfenderUmstand):
    __tablename__='ursache'

    __mapper_args__ = {
    'polymorphic_identity':'ursache',
    }      

    def add(krankheit_name, ursache_name):
        ursache=session.query(Ursache).filter(Ursache.name==ursache_name).first() #query1 schemaelement
        if ursache is None:
            ursache=Ursache(name=ursache_name) #2 anlegen von schemaelement fals noch nicht vorhanden
            session_add_and_commit(ursache)
        krankheit_ursachen=Ursache.getAll_fromKrankheit(krankheit_name, False) #3 get all schemaelements von kh
        krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first() #4 query krankheit
        krankheit_ursachen.append(ursache)
        krankheit.ursachen=krankheit_ursachen
        session.commit()
    
    def changeall(krankheit_name, ursache_name, ursache4change):
        ursache=session.query(Ursache).filter(Ursache.name==ursache4change).first()
        ursache2change=session.query(Ursache).filter(Ursache.name==ursache_name).first()
        if ursache2change is not None: #None=> ursache2change = Krankheit
            if ursache is None:
                ursache2change.name=ursache4change
                session_add_and_commit(ursache2change)
            else:
                print('existing=%s new=%s'%(ursache2change.name, ursache.name))
                ursache2change=session.merge(ursache)
                print('existing=%s new=%s'%(ursache2change.name, ursache.name))
                session.commit()
    
    def changeone(krankheit_name, ursache_name, ursache4change):
        ursache=session.query(Ursache).filter(Ursache.name==ursache_name).first()
        krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
        new_ursache=session.query(Ursache).filter(Ursache.name==ursache4change).first()
        if new_ursache is None: # new_ursache not existing
            new_ursache=Ursache(name=ursache4change)
        krankheit_ursachen=Ursache.getAll_fromKrankheit(krankheit_name, False)
        krankheit_ursachen.remove(ursache)
        krankheit_ursachen.append(new_ursache)
        krankheit.ursachen=krankheit_ursachen
        session.commit()
    
    def deleteall(krankheit_name, ursache_name):
        ursache2delete=session.query(Ursache).filter(Ursache.name==ursache_name).first()
        if ursache2delete is not None:
            session.delete(ursache2delete)
            session.commit()

    def deleteone(krankheit_name, ursache_name):
        ursache=session.query(Ursache).filter(Ursache.name==ursache_name).first()
        if ursache is not None:
            krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
            krankheit_ursachen=Ursache.getAll_fromKrankheit(krankheit_name, False)
            krankheit_ursachen.remove(ursache)
            krankheit.ursachen=krankheit_ursachen
        else:
            krankheit=session.query(Krankheit).filter(Krankheit.name==ursache_name).first()
            ursache_kh=session.query(Ursache).filter(Ursache.krankheit_id==krankheit.id).first()
            ursachen=Ursache.getAll_fromKrankheit(krankheit_name, False)
            ursachen.remove(ursache_kh)
            krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
            krankheit.ursachen=ursachen
            session.commit()

    def getAll_fromKrankheit(krankheit_name, toString=False):
        krankheit_ursachen=[]
        try:
            krankheit=session.query(Krankheit).join(Krankheit.ursachen).filter(Krankheit.name==krankheit_name).first()
            for ursache in krankheit.ursachen:
                krankheit_ursachen.append(ursache)
            if toString==True:
                ursachenstrings=[]
                for ursache in krankheit_ursachen:
                    if ursache.name is None:
                        ursache=session.query(Krankheit).filter(Krankheit.id==ursache.krankheit_id).first()
                    ursachenstrings.append(ursache.name)
                krankheit_ursachen=ursachenstrings
        except AttributeError:
            krankheit_ursachen=[]
        return krankheit_ursachen

    def getAll():
        elemente=[]
        elementesql=session.query(Ursache).all()
        for element in elementesql:
            if element.name==None:
                element=session.query(Krankheit).filter(Krankheit.id==element.krankheit_id).first()
            elemente.append(element.name)
        return elemente

    def addKrankheit(krankheit_name, krankheit2add):
        """fügt bei Ursachen eine Krankheit hinzu"""
        krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit2add).first()
        ursache_kh=session.query(Ursache).filter(Ursache.krankheit_id==krankheit.id).first()
        if ursache_kh is None:
            ursache_kh=Ursache(krankheit_id=krankheit.id)
            session_add_and_commit(ursache_kh)
        ursachen=Ursache.getAll_fromKrankheit(krankheit_name, False)
        krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
        ursachen.append(ursache_kh)
        krankheit.ursachen=ursachen
        session.commit()
        
class Symptom(Umstand):
    __tablename__='symptom'
    
    __mapper_args__ = {
    'polymorphic_identity':'symptom',
    }
    def queryfromclass():
        super(Symptom,Symptom).queryfromclass()
    def link_Content2krankheit(krankheit, content):
        super(Symptom,Symptom).link_Content2krankheit(krankheit, content)
    def get_contentfromkrankheit(krankheit):
        super(Symptom,Symptom).get_contentfromkrankheit(krankheit)
    def new_Object(object_name):
        super(Symptom,Symptom).new_Object(object_name)
    def getelems_from_krankheit2umstand(krankheit):
        super(Symptom,Symptom).getelems_from_krankheit2umstand(krankheit)
    def add(krankheit_name, element_name):
        super(Symptom,Symptom).add(krankheit_name, element_name)
    def getAll_fromKrankheit(krankheit_name, toString=False):
        super(Symptom,Symptom).getAll_fromKrankheit(krankheit_name, toString=False)
    def getAll():
        super(Symptom,Symptom).getAll()

class Komplikation(VerknüpfenderUmstand):
    __tablename__='komplikation'

    __mapper_args__ = {
    'polymorphic_identity':'komplikation',
    }
    def queryfromclass():
        super(Komplikation).queryfromclass()
    def link_Content2krankheit(krankheit, content):
        super(Komplikation).link_Content2krankheit(krankheit, content)
    def get_contentfromkrankheit(krankheit):
        super(Komplikation).get_contentfromkrankheit(krankheit)
    def new_Object(object_name):
        super(Komplikation).new_Object(object_name)
    def getelems_from_krankheit2umstand(krankheit):
        super(Komplikation).getelems_from_krankheit2umstand(krankheit)
    def add(krankheit_name, element_name):
        super(Komplikation).add(krankheit_name, element_name)
    def getAll_fromKrankheit(krankheit_name, toString=False):
        super(Komplikation).getAll_fromKrankheit(krankheit_name, toString=False)
    def getAll():
        super(Komplikation).getAll()

    def addKrankheit(krankheit_name, krankheit2add):
        """fügt bei Komplikationen eine Krankheit hinzu"""
        krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit2add).first()
        komplikation_kh=session.query(Komplikation).filter(Komplikation.krankheit_id==krankheit.id).first()
        if komplikation_kh is None:
            komplikation_kh=Komplikation(krankheit_id=krankheit.id)
            session_add_and_commit(komplikation_kh)
        komplikationen=Komplikation.getAll_fromKrankheit(krankheit_name, False)
        krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
        komplikationen.append(komplikation_kh)
        krankheit.komplikationen=komplikationen
        session.commit()

class Diagnostik(Umstand):
    __tablename__='diagnostik'

    __mapper_args__ = {
    'polymorphic_identity':'diagnostik',
    }
    def queryfromclass():
        super(Diagnostik).queryfromclass()
    def link_Content2krankheit(krankheit, content):
        super(Diagnostik).link_Content2krankheit(krankheit, content)
    def get_contentfromkrankheit(krankheit):
        super(Diagnostik).get_contentfromkrankheit(krankheit)
    def new_Object(object_name):
        super(Diagnostik).new_Object(object_name)
    def getelems_from_krankheit2umstand(krankheit):
        super(Diagnostik).getelems_from_krankheit2umstand(krankheit)
    def add(krankheit_name, element_name):
        super(Diagnostik).add(krankheit_name, element_name)
    def getAll_fromKrankheit(krankheit_name, toString=False):
        super(Diagnostik).getAll_fromKrankheit(krankheit_name, toString=False)
    def getAll():
        super(Diagnostik).getAll()

class Therapie(Umstand):
    __tablename__='therapie'

    __mapper_args__ = {
    'polymorphic_identity':'therapie',
    }
    def queryfromclass():
        super(Therapie).queryfromclass()
    def link_Content2krankheit(krankheit, content):
        super(Therapie).link_Content2krankheit(krankheit, content)
    def get_contentfromkrankheit(krankheit):
        super(Therapie).get_contentfromkrankheit(krankheit)
    def new_Object(object_name):
        super(Therapie).new_Object(object_name)
    def getelems_from_krankheit2umstand(krankheit):
        super(Therapie).getelems_from_krankheit2umstand(krankheit)
    def add(krankheit_name, element_name):
        super(Therapie).add(krankheit_name, element_name)
    def getAll_fromKrankheit(krankheit_name, toString=False):
        super(Therapie).getAll_fromKrankheit(krankheit_name, toString=False)
    def getAll():
        super(Therapie).getAll()

Base.metadata.create_all(engine)

def session_add_and_commit(new_obj_name):
    session.add(new_obj_name)
    session.commit()

def data4fragen2dict(krankheitenliste):
    krankheitendicts4fragen=[]
    schemas=['Ursachen','Symptome','Komplikationen','Diagnostiken','Therapien']
    for krankheit in krankheitenliste:
        krankheitendict4fragen={'Krankheit':krankheit}
        for schema in schemas:
            krankheitendict4fragen[schema]={'Right':[],'Wrong':[]}
            if schema=='Ursachen':
                schemaRights=Ursache.getAll_fromKrankheit(krankheit, True)
                schemaAll=Ursache.getAll()
            elif schema=='Symptome':
                schemaRights=Symptom.getAll_fromKrankheit(krankheit, True)
                schemaAll=Symptom.getAll()
            elif schema=='Komplikationen':
                schemaRights=Komplikation.getAll_fromKrankheit(krankheit, True)
                schemaAll=Komplikation.getAll()
            elif schema=='Diagnostiken':
                schemaRights=Diagnostik.getAll_fromKrankheit(krankheit, True)
                schemaAll=Diagnostik.getAll()
            elif schema=='Therapien':
                schemaRights=Therapie.getAll_fromKrankheit(krankheit, True)
                schemaAll=Therapie.getAll()
            for element in schemaRights:
                krankheitendict4fragen[schema]['Right'].append(element)
                if element in schemaAll:
                    schemaAll.remove(element)
            if krankheit in schemaAll:
                schemaAll.remove(krankheit)
            for element in schemaAll:
                krankheitendict4fragen[schema]['Wrong'].append(element)
        krankheitendicts4fragen.append(krankheitendict4fragen)
    return krankheitendicts4fragen

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

def relationIDupdate(keepID, deleteID, schema):
    query='UPDATE kh2%s SET %s_id=%s WHERE %s_id == %s'%(schema, schema, keepID, schema, deleteID)
    querytext=text(query)
    connection.execute(querytext)
    session.commit()

def relationIDselect(schema, id):
    query='SELECT %s_id FROM kh2%s WHERE %s_id == %d'%(schema,schema,schema,id)
    querytext=text(query)
    print(connection.execute(querytext).fetchall())

# look4AlikesinDB()
# relationIDselect('therapie', 28)
# relationIDupdate(38, 28, 'therapie')
# relationIDselect('therapie', 28)



# for element in elements:
#     if element.name == 'Übergewichtig':
#         id=element.id

# def uok_addKrankheit(schema_name, krankheit_name, krankheit2add):
#     """fügt bei Ursachen oder Komplikationen Krankheiten hinzu"""
#     krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
#     schemacontent=kh_SchemaContentGetall(krankheit_name, schema_name, False)
#     if schema_name=='Ursachen':
#         new_schemacontent=session.query(Krankheit).filter(Krankheit.name==krankheit2add).first()
#         schemacontent.append(new_schemacontent)
#         krankheit.ursachen=schemacontent
#     elif schema_name=='Komplikationen':
#         new_schemacontent=session.query(Krankheit).filter(Krankheit.name==krankheit2add).first()
#         schemacontent.append(new_schemacontent)
#         krankheit.komplikationen=schemacontent
#     session.commit() #hier scheitert es wahrscheinlich, weil es nicht mit dem Objekt Krankheit rechnet -> mit TextSql händisch Ids verbinden?

# def uok_addKrankheit_text(schema_name, krankheit_name, krankheit2add):
#     """fügt bei Ursachen oder Komplikationen Krankheiten hinzu"""
#     sqladdrelation("krankheiten","krankheiten",krankheit2add, krankheit_name, "kh2%s"%(schema_name.lower()),True)

# def kh_getAll_text(table, column='name', join_table='', join_column='', condition=''):
#     """table->'tablename', column->'columnname', join_table->'tablename', join_column->'columnname', 
#     condition->'Krankheiten.name==krankheit_name'"""
#     join=''
#     where=''
#     if join_table != '' and join_column != '':
#         join='JOIN %s.%s'%(join_table,join_column)
#     if where != '':
#         where='WHERE %s'%(condition)
#     result=sqlselectAll("SELECT %s FROM %s %s %s"%(column, table, join, where))
#     return result

   
# # krankheit_ursachen=session.query(Krankheit).join(Krankheit.ursachen).filter(Krankheit.name=='Arteriosklerose').first()
# # krankheit_symptome=session.query(Krankheit).join(Krankheit.symptome).filter(Krankheit.name=='Arteriosklerose').first()
# # krankheit_komplikationen=session.query(Krankheit).join(Krankheit.komplikationen).filter(Krankheit.name=='Arteriosklerose').first()
# # krankheit_diagnostiken=session.query(Krankheit).join(Krankheit.diagnostiken).filter(Krankheit.name=='Arteriosklerose').first()
# # krankheit_therapien=session.query(Krankheit).join(Krankheit.therapien).filter(Krankheit.name=='Arteriosklerose').first()

# # for therapien in krankheit_therapien:
# #     print(therapien) 

# #######################
# #SQL-TEXT-Functions
# #######################

# def sqladd(query):
#     """Query like: 'INSERT INTO table (column1,..) VALUES(value1,..)
#     without return"""
#     querytext=text(query)
#     connection.execute(querytext)
#     session.commit()

# def sqlGetid(table_name, value_name, column_name='name'):
#     """"""
#     query="SELECT id FROM %s WHERE %s='%s'"%(table_name,column_name,value_name)
#     result=sqlselectOne(query)
#     return result

# def sqladdrelation(table1, table2, value1, value2, relation_table, kh_uok_relation=False):
#     """Fügt in relation_table im Column table1_id und table2_id die jeweiligen ids ein
#     kh_uok_relation True: Verbindung von Krankheiten -> uok"""
#     kh_uok_string=''
#     if kh_uok_relation is True:
#         kh_uok_string='_kh'
#     id1=sqlGetid(table1, value1)
#     id2=sqlGetid(table2, value2)
#     query="INSERT INTO %s (%s_id, %s_id%s) VALUES ('%s', '%s')"%(relation_table, table1, table2, kh_uok_string, id1, id2)
#     sqladd(query)   

# def sqlselectAll(query):
#     """Query like: 'SELECT column FROM table INNER JOIN table.column WHERE condition'
#     returns with fetchall() 
#     """
#     querytext=text(query)
#     result=connection.execute(querytext).fetchall()
#     list_result=[]
#     for row in result:
#         (element,) = row
#         list_result.append(element)
#     return list_result

# def sqlselectOne(query):
#     """Query like: 'SELECT column FROM table INNER JOIN table.column WHERE condition'
#     returns with fetchone()
#     """
#     querytext=text(query)
#     (result,)=connection.execute(querytext).fetchone()
#     return result

# # def krankheit_getSchemacontent(schema_name, krankheit_name, where=''):
# #     "where like: 'WHERE krankheiten.name='Arteriosklerose''"
# #     query=("SELECT %s.name FROM krankheiten INNER JOIN %s %s"%(schema_name, schema_name, where))
# #     result=sqlselectAll(query)
# #     return result