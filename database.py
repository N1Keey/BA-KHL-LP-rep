from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Table, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

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

class Role(Base):
    __tablename__='roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)
    description = Column(String(255))

relation = Table('relation', Base.metadata,
    Column('krankheit_id', Integer, ForeignKey('krankheiten.id', ondelete="CASCADE")),
    Column('ursache_id', Integer, ForeignKey('ursachen.id', ondelete="CASCADE")),
    Column('symptom_id', Integer, ForeignKey('symptome.id', ondelete="CASCADE")),
    Column('komplikation_id', Integer, ForeignKey('komplikationen.id', ondelete="CASCADE")),
    Column('diagnostik_id', Integer, ForeignKey('diagnostiken.id', ondelete="CASCADE")),
    Column('therapie_id', Integer, ForeignKey('therapien.id', ondelete="CASCADE"))
    )

class Krankheit(Base):
    __tablename__='krankheiten'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)
    beschreibung = Column(String(255), default='Leer')
    ursachen = relationship('Ursache', secondary=relation)
    symptome = relationship('Symptom', secondary=relation)
    komplikationen = relationship('Komplikation', secondary=relation)
    diagnostiken = relationship('Diagnostik', secondary=relation)
    therapien = relationship('Therapie', secondary=relation)

class Ursache(Base):
    __tablename__='ursachen'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

class Symptom(Base):
    __tablename__='symptome'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

class Komplikation(Base):
    __tablename__='komplikationen'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

class Diagnostik(Base):
    __tablename__='diagnostiken'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

class Therapie(Base):
    __tablename__='therapien'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

Base.metadata.create_all(engine)

def user_regist(user_email, user_password):
    """Adds User to Database and gives the standard-role: 'User'
    """
    new_User=User(email=user_email, password=user_password)
    new_user_role=session.query(Role).filter(Role.name=='User').first()
    new_User.roles=[new_user_role]
    session.add(new_User)
    session.commit()

def user_login(user_email, user_password):
    """returns True if Email exists and Password is right
    False if Email isnt existing or Password isnt right
    """
    login_bool=False
    users=session.query(User)
    for user in users:
        if user_email==user.email and user_password==user.password:
            login_bool=True
    return login_bool

def user_getall2Dict():
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

def user_delete(user_ID):
    """Deletes User with given user_ID"""
    user=session.query(User).filter(User.id==user_ID)
    if user.first().email != 'Nschick@mail.hs-ulm.de':
        user.delete()
        session.commit()

def role_add(role_name, role_description):
    """Adds Role to Database"""
    new_Role=Role(name=role_name, description=role_description)
    session.add(new_Role)
    session.commit()

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

def krankheiten_add(krankheit_name):
    new_Krankheit=Krankheit(name=krankheit_name)
    session.add(new_Krankheit)
    session.commit()

#######################
#SQL-TEXT-Functions
#######################

def sqladd(query):
    """Query like: 'INSERT INTO table (column1,..) VALUES(value1,..)
    without return"""
    querytext=text(query)
    connection.execute(querytext)
    connection.commit()

def sqlgetid(table_name, value_name, column_name='name'):
    query="SELECT id FROM %s WHERE %s='%s'"%(table_name,column_name,value_name)
    id_=sqlselect(query)
    return id_

def sqladdrelation(table1, table2, value1, value2, relation_table):
    id1=sqlgetid(table1, value1)
    id2=sqlgetid(table2, value2)
    query="INSERT INTO %s (%s_id, %s_id) VALUES ('%s', '%s')"%(relation_table, table1, table2, id1, id2)
    sqladd(query)   

def sqlselect(query):
    """Query like: 'SELECT column FROM table INNER JOIN table.column WHERE condition'
    returns with fetchall()
    """
    querytext=text(query)
    result=connection.execute(querytext).fetchall()
    return result

def krankheit_add_schema(krankheit_name, schema_name, schema_eigenschaft):
    """Adds Schema zur Datenbank und zur Krankheit"""
    where='WHERE %s.name = %s'%(schema_name, schema_eigenschaft)
    kh_sch_content=krankheit_getSchemacontent(schema_name,krankheit_name,where=where)
    if kh_sch_content==[]:
        query="INSERT INTO %s (name) VALUES(%s) "%(schema_name, schema_eigenschaft)
        sqladd(query)
    sqladdrelation('krankheiten', schema_name, krankheit_name, schema_eigenschaft, 'relation')

def krankheit_multifunct(krankheit_name=None, schema_name=None, where=None, schema_eigenschaft=None):
    bla='hose'
    return bla

def krankheit_getSchemacontent(schema_name, krankheit_name, where=''):
    "where like: 'WHERE krankheiten.name='Arteriosklerose''"
    query=("SELECT %s.name FROM krankheiten INNER JOIN %s %s"%(schema_name, schema_name, where))
    result=sqlselect(query)
    return result

def krankheiten_getall():
    krankheiten=session.query(Krankheit).all()
    # for krankheit in krankheiten:
        
def krankheiten_getall2Dict():
    """
    """
    krankheitendicts=[]

    krankheiten=session.query(Krankheit).all()

    for krankheit in krankheiten:
        krankheitdict={'Krankheit':krankheit.name, 'Beschreibung':krankheit.beschreibung}
        krankheitendicts.append(krankheitdict)
    return krankheitendicts

        # ursache_list=[] 
        # for ursache in krankheit.ursachen:
        #     ursache_list.append(ursache.name)
        # krankheitdict['Ursachen']=ursache_list
        
        # symptom_list=[] 
        # for symptom in krankheit.symptome:
        #     symptom_list.append(symptom.name)
        # krankheitdict['Symptome']=symptom_list
        
        # komplikation_list=[] 
        # for komplikation in krankheit.komplikationen:
        #     komplikation_list.append(komplikation.name)
        # krankheitdict['Komplikationen']=komplikation_list
        
        # diagnostik_list=[] 
        # for diagnostik in krankheit.diagnostiken:
        #     diagnostik_list.append(diagnostik.name)
        # krankheitdict['Diagnostik']=diagnostik_list
        
        # therapie_list=[] 
        # for therapie in krankheit.therapien:
        #     therapie_list.append(therapie.name)
        # krankheitdict['Therapie']=therapie_list
        