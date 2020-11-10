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

kh2ursachen = Table('kh2ursachen', Base.metadata,
    Column('krankheiten_id', Integer, ForeignKey('krankheiten.id', ondelete="CASCADE")),
    Column('ursachen_id', Integer, ForeignKey('ursachen.id', ondelete="CASCADE")),
    Column('krankheiten_id_', Integer, ForeignKey('krankheiten.id', ondelete="CASCADE")),
    )
kh2symptome = Table('kh2symptome', Base.metadata,
    Column('krankheiten_id', Integer, ForeignKey('krankheiten.id', ondelete="CASCADE")),
    Column('symptome_id', Integer, ForeignKey('symptome.id', ondelete="CASCADE")),
    )
kh2komplikationen = Table('kh2komplikationen', Base.metadata,
    Column('krankheiten_id', Integer, ForeignKey('krankheiten.id', ondelete="CASCADE")),
    Column('komplikationen_id', Integer, ForeignKey('komplikationen.id', ondelete="CASCADE")),
    Column('krankheiten_id_', Integer, ForeignKey('krankheiten.id', ondelete="CASCADE")),
    )
kh2diagnostiken = Table('kh2diagnostiken', Base.metadata,
    Column('krankheiten_id', Integer, ForeignKey('krankheiten.id', ondelete="CASCADE")),
    Column('diagnostiken_id', Integer, ForeignKey('diagnostiken.id', ondelete="CASCADE")),
    )
kh2therapien = Table('kh2therapien', Base.metadata,
    Column('krankheiten_id', Integer, ForeignKey('krankheiten.id', ondelete="CASCADE")),
    Column('therapien_id', Integer, ForeignKey('therapien.id', ondelete="CASCADE"))
    )

class Krankheit(Base):
    __tablename__='krankheiten'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)
    ursachen = relationship('Ursache', secondary=kh2ursachen)
    symptome = relationship('Symptom', secondary=kh2symptome)
    komplikationen = relationship('Komplikation', secondary=kh2komplikationen)
    diagnostiken = relationship('Diagnostik', secondary=kh2diagnostiken)
    therapien = relationship('Therapie', secondary=kh2therapien)

class Ursache(Base):
    __tablename__='ursachen'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)
    krankheiten = relationship('Krankheit', secondary=kh2ursachen)

class Symptom(Base):
    __tablename__='symptome'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

class Komplikation(Base):
    __tablename__='komplikationen'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)
    krankheiten = relationship('Krankheit', secondary=kh2komplikationen)

class Diagnostik(Base):
    __tablename__='diagnostiken'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

class Therapie(Base):
    __tablename__='therapien'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

Base.metadata.create_all(engine)

def session_add_and_commit(new_obj_name):
    session.add(new_obj_name)
    session.commit()

def kh_addKrankheit(krankheit_name):
    """Adds Krankheiten 2 db"""
    new_Krankheit=Krankheit(name=krankheit_name)
    session_add_and_commit(new_Krankheit)

def kh_addSchema(krankheit_name, schema_name, eigenschaft_name): #Wenn Eigenschaft schon vorhanden verbinde vorhandenes mit Krankheit -> fehlt noch
    """Adds Eigenschaften von Krankheiten 2 Schema in db"""
    if schema_name=='Ursachen':
        new_Object=Ursache(name=eigenschaft_name)
    elif schema_name=='Symptome':
        new_Object=Symptom(name=eigenschaft_name)
    elif schema_name=='Komplikationen':
        new_Object=Komplikation(name=eigenschaft_name)
    elif schema_name=='Diagnostiken':
        new_Object=Diagnostik(name=eigenschaft_name)
    elif schema_name=='Therapien':
        new_Object=Therapie(name=eigenschaft_name)
    session_add_and_commit(new_Object)
    schema2krankheit(krankheit_name,schema_name,eigenschaft_name)

def schema2krankheit(krankheit_name, schema_name, eigenschaft_name):
    """Verbindet Eigenschaft mit Krankheit"""
    krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
    schemacontent=kh_SchemaContentGetall(krankheit_name, schema_name, False)
    if schema_name=='Ursachen':
        new_schemacontent=session.query(Ursache).filter(Ursache.name==eigenschaft_name).first()
        schemacontent.append(new_schemacontent)
        krankheit.ursachen=schemacontent
    elif schema_name=='Symptome':
        new_schemacontent=session.query(Symptom).filter(Symptom.name==eigenschaft_name).first()
        schemacontent.append(new_schemacontent)
        krankheit.symptome=schemacontent
    elif schema_name=='Komplikationen':
        new_schemacontent=session.query(Komplikation).filter(Komplikation.name==eigenschaft_name).first()
        schemacontent.append(new_schemacontent)
        krankheit.komplikationen=schemacontent
    elif schema_name=='Diagnostiken':
        new_schemacontent=session.query(Diagnostik).filter(Diagnostik.name==eigenschaft_name).first()
        schemacontent.append(new_schemacontent)
        krankheit.diagnostiken=schemacontent
    elif schema_name=='Therapien':
        new_schemacontent=session.query(Therapie).filter(Therapie.name==eigenschaft_name).first()
        schemacontent.append(new_schemacontent)
        krankheit.therapien=schemacontent
    session.commit()

def kh_Krankheiten_getall():
    """Get all Krankheiten"""
    krankheiten=[]
    sqlelement=session.query(Krankheit).order_by(Krankheit.id.asc()).all()
    for row in sqlelement:
        krankheiten.append(row.name)
    return krankheiten

def kh_SchemaContentGetall(krankheit_name, schema_name, toString):
    """Get Eigenschaften aus Schema von Krankheit
    toString True -> packt die Liste der Objekte in eine Stringliste mit den Namen der Objekte"""
    schemacontent=[]
    try:
        if schema_name=='Ursachen':
            schema_query=session.query(Krankheit).join(Krankheit.ursachen).filter(Krankheit.name==krankheit_name).first()
            for element in schema_query.ursachen:
                schemacontent.append(element)
        elif schema_name=='Symptome':
            schema_query=session.query(Krankheit).join(Krankheit.symptome).filter(Krankheit.name==krankheit_name).first()
            for element in schema_query.symptome:
                schemacontent.append(element)
        elif schema_name=='Komplikationen':
            schema_query=session.query(Krankheit).join(Krankheit.komplikationen).filter(Krankheit.name==krankheit_name).first()
            for element in schema_query.komplikationen:
                schemacontent.append(element)
        elif schema_name=='Diagnostiken':
            schema_query=session.query(Krankheit).join(Krankheit.diagnostiken).filter(Krankheit.name==krankheit_name).first()
            for element in schema_query.diagnostiken:
                schemacontent.append(element)
        elif schema_name=='Therapien':
            schema_query=session.query(Krankheit).join(Krankheit.therapien).filter(Krankheit.name==krankheit_name).first()
            for element in schema_query.therapien:
                schemacontent.append(element)
        if toString==True:
            contentstrings=[]
            for element in schemacontent:
                contentstrings.append(element.name)
            schemacontent=contentstrings
    except AttributeError:
        schemacontent=[]
    return schemacontent

def uok_addKrankheit(schema_name, krankheit_name, krankheit2add):
    """fügt bei Ursachen oder Komplikationen Krankheiten hinzu"""
    krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
    schemacontent=kh_SchemaContentGetall(krankheit_name, schema_name, False)
    if schema_name=='Ursachen':
        new_schemacontent=session.query(Krankheit).filter(Krankheit.name==krankheit2add).first()
        schemacontent.append(new_schemacontent)
        krankheit.ursachen=schemacontent
    elif schema_name=='Komplikationen':
        new_schemacontent=session.query(Krankheit).filter(Krankheit.name==krankheit2add).first()
        schemacontent.append(new_schemacontent)
        krankheit.komplikationen=schemacontent
    session.commit() #hier scheitert es wahrscheinlich, weil es nicht mit dem Objekt Krankheit rechnet -> mit TextSql händisch Ids verbinden?

def uok_addKrankheit_text(schema_name, krankheit_name, krankheit2add):
    """fügt bei Ursachen oder Komplikationen Krankheiten hinzu"""
    sqladdrelation("krankheiten","krankheiten",krankheit2add, krankheit_name, "kh2%s"%(schema_name.lower()))


#######################
#SQL-TEXT-Functions
#######################

def sqladd(query):
    """Query like: 'INSERT INTO table (column1,..) VALUES(value1,..)
    without return"""
    querytext=text(query)
    connection.execute(querytext)
    session.commit()

def sqlGetid(table_name, value_name, column_name='name'):
    """"""
    query="SELECT id FROM %s WHERE %s='%s'"%(table_name,column_name,value_name)
    result=sqlselectOne(query)
    id_=result[0]
    id__=id_[0]
    return id__

def sqladdrelation(table1, table2, value1, value2, relation_table):
    id1=sqlGetid(table1, value1)
    id2=sqlGetid(table2, value2)
    query="INSERT INTO %s (%s_id_, %s_id) VALUES ('%s', '%s')"%(relation_table, table1, table2, id1, id2)
    sqladd(query)   

# def sqlselectAll(query):
#     """Query like: 'SELECT column FROM table INNER JOIN table.column WHERE condition'
#     returns with fetchall() 
#     """
#     querytext=text(query)
#     result=connection.execute(querytext).fetchall()
#     return result

def sqlselectOne(query):
    """Query like: 'SELECT column FROM table INNER JOIN table.column WHERE condition'
    returns with fetchall()
    """
    querytext=text(query)
    result=connection.execute(querytext).fetchall()
    return result

# def krankheit_getSchemacontent(schema_name, krankheit_name, where=''):
#     "where like: 'WHERE krankheiten.name='Arteriosklerose''"
#     query=("SELECT %s.name FROM krankheiten INNER JOIN %s %s"%(schema_name, schema_name, where))
#     result=sqlselectAll(query)
#     return result