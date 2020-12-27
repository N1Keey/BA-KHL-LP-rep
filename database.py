from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Table, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json

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
                if ursache is not None:
                    if ursache.name is None:
                        ursache=session.query(Krankheit).filter(Krankheit.id==ursache.krankheit_id).first()
                    ursachen.append(ursache.name)
            krankheitendict['Ursachen']=ursachen
            symptome=[]
            for symptom in krankheit.symptome:
                symptome.append(symptom.name)
            krankheitendict['Symptome']=symptome
            komplikationen=[]
            for komplikation in krankheit.komplikationen:
                if komplikation is not None:
                    if komplikation.name is None:
                            komplikation=session.query(Krankheit).filter(Krankheit.id==komplikation.krankheit_id).first()
                    komplikationen.append(komplikation.name)
            krankheitendict['Komplikationen']=komplikationen
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

    def change(krankheit_name, new_name):
        element2change=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
        element2change.name=new_name
        session_add_and_commit(element2change)       
    
    def delete(krankheit_name):
        element2delete=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
        session.delete(element2delete)
        session.commit()

class Umstand(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

    @property
    def getname(self):
        return self.name

    def add(_class, krankheit_name, element_name):
        if issubclass(_class, Umstand):
            element=session.query(_class).filter(_class.name==element_name).first() #query1 schemaelement
            if element is None:
                element=_class(name=element_name) #2 anlegen von schemaelement fals noch nicht vorhanden
                session_add_and_commit(element)
            krankheit_elemente=_class.getAll_fromKrankheit(_class, krankheit_name, False) #3 get all schemaelements von kh
            krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first() #4 query krankheit
            krankheit_elemente.append(element)
            setkh_Umstand_elemente(_class.__name__, krankheit, krankheit_elemente)
            session.commit()
        else:
            pass # Fehlermeldung

    def getAll(_class):
        if issubclass(_class, Umstand):
            elemente=[]
            elementesql=session.query(_class).all()
            for element in elementesql:
                if element.name==None:
                    element=session.query(Krankheit).filter(Krankheit.id==element.krankheit_id).first()
                elemente.append(element.name)
            return elemente
        else:
            pass # Fehlermeldung

    def getAll_fromKrankheit(_class, krankheit_name, toString=False):
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
                        if element.name is None:
                            element=session.query(Krankheit).filter(Krankheit.id==element.krankheit_id).first()
                        if element is not None:  
                            elementstrings.append(element.name)
                    krankheit_elemente=elementstrings
            return krankheit_elemente
        else:
            pass # Fehlermeldung

    def changeall(_class, krankheit_name, element_name, newElement_name):
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
                if new_element is None: # new_element not existing
                    new_element=_class(name=newElement_name)  
            else:
                new_element=new_kh_element       
            krankheit_elemente.append(new_element)
            setkh_Umstand_elemente(_class.__name__, krankheit, krankheit_elemente)
            session.commit()
        else:
            pass # Fehlermeldung

    def deleteall(_class, krankheit_name, element_name):
        if issubclass(_class, Umstand):
            element2delete=session.query(_class).filter(_class.name==element_name).first()
            if element2delete is None: #=> element2delete=Krankheit
                element2delete=session.query(Krankheit).filter(Krankheit.name==element_name).first()   
            session.delete(element2delete)
            session.commit()
        else:
            pass # Fehlermeldung

    def deleteone(_class, krankheit_name, element2del_name):
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

    __mapper_args__ = {
    'polymorphic_identity':'umstand',
    'polymorphic_on':type
    }

class VerknüpfenderUmstand(Umstand):
    __abstract__ = True
    krankheit_id = Column(Integer, unique=True)

    @property
    def getname(self):
        if self.krankheit_id is None:
            return super().name
        else:
            pass # lookup
    #u.name

    def getname(self, name):
        self.name = name        

    def addKrankheit(_class, krankheit_name, krankheit2add):
        """fügt eine Krankheit hinzu"""
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
    krankheit_id = Column(Integer, unique=True)

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

def fragendicts2json(dicts):
    jsondict = json.dumps(dicts,ensure_ascii=False,)
    with open("fragen.json","w", encoding='utf-8') as fw:
        fw.write(jsondict)

def json2fragendicts():
    with open('fragen.json','r',encoding='utf-8') as fr:
        jsonstring=fr.read()
        dicts=json.loads(jsonstring)
    return dicts
    
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
                schemaRights=Ursache.getAll_fromKrankheit(Ursache,krankheit, True)
                schemaAll=Ursache.getAll(Ursache)
            elif schema=='Symptome':
                schemaRights=Symptom.getAll_fromKrankheit(Symptom,krankheit, True)
                schemaAll=Symptom.getAll(Symptom)
            elif schema=='Komplikationen':
                schemaRights=Komplikation.getAll_fromKrankheit(Komplikation,krankheit, True)
                schemaAll=Komplikation.getAll(Komplikation)
            elif schema=='Diagnostiken':
                schemaRights=Diagnostik.getAll_fromKrankheit(Diagnostik,krankheit, True)
                schemaAll=Diagnostik.getAll(Diagnostik)
            elif schema=='Therapien':
                schemaRights=Therapie.getAll_fromKrankheit(Therapie,krankheit, True)
                schemaAll=Therapie.getAll(Therapie)
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