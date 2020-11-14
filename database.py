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

class Ursache(Base):
    __tablename__='ursache'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

class Symptom(Base):
    __tablename__='symptom'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

class Komplikation(Base):
    __tablename__='komplikation'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

class Diagnostik(Base):
    __tablename__='diagnostik'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)

class Therapie(Base):
    __tablename__='therapie'
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

def kh_addSchemacontent(krankheit_name, schema_name, eigenschaft_name): #Wenn Eigenschaft schon vorhanden verbinde vorhandenes mit Krankheit -> fehlt noch
    """Adds Eigenschaften von Krankheiten 2 Schema in db"""
    if schema_name=='Ursachen':
        new_Object=Ursache(name=eigenschaft_name)
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

def kh_Krankheiten_getall_text():
    """Get all Krankheiten"""
    krankheiten=kh_getAll_text('krankheiten')
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

def symptom_add(krankheit_name, symptom_name): #Wenn Eigenschaft schon vorhanden verbinde vorhandenes mit Krankheit -> fehlt noch
    symptom=Symptom(name=symptom_name)
    session_add_and_commit(symptom)
    symptom2krankheit(krankheit_name, symptom)

def symptom2krankheit(krankheit_name, symptom):
    krankheit=session.query(Krankheit).filter(Krankheit.name==krankheit_name).first()
    krankheit_symptome=symptome_getAll_fromKrankheit(krankheit_name, False)
    krankheit_symptome.append(symptom)
    krankheit.symptome=krankheit_symptome

def symptome_getAll_fromKrankheit(krankheit_name, toString=False):
    krankheit_symptome=[]
    try:
        krankheit=session.query(Krankheit).join(Krankheit.symptome).filter(Krankheit.name==krankheit_name).first()
        for symptom in krankheit.symptome:
            krankheit_symptome.append(symptom)
        if toString==True:
            symptomestrings=[]
            for symptom in krankheit_symptome:
                symptomestrings.append(symptom.name)
            krankheit_symptome=symptomestrings
    except AttributeError:
        krankheit_symptome=[]
    return krankheit_symptome

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
    sqladdrelation("krankheiten","krankheiten",krankheit2add, krankheit_name, "kh2%s"%(schema_name.lower()),True)

def kh_getAll_text(table, column='name', join_table='', join_column='', condition=''):
    """table->'tablename', column->'columnname', join_table->'tablename', join_column->'columnname', 
    condition->'Krankheiten.name==krankheit_name'"""
    join=''
    where=''
    if join_table != '' and join_column != '':
        join='JOIN %s.%s'%(join_table,join_column)
    if where != '':
        where='WHERE %s'%(condition)
    result=sqlselectAll("SELECT %s FROM %s %s %s"%(column, table, join, where))
    return result

   
# krankheit_ursachen=session.query(Krankheit).join(Krankheit.ursachen).filter(Krankheit.name=='Arteriosklerose').first()
# krankheit_symptome=session.query(Krankheit).join(Krankheit.symptome).filter(Krankheit.name=='Arteriosklerose').first()
# krankheit_komplikationen=session.query(Krankheit).join(Krankheit.komplikationen).filter(Krankheit.name=='Arteriosklerose').first()
# krankheit_diagnostiken=session.query(Krankheit).join(Krankheit.diagnostiken).filter(Krankheit.name=='Arteriosklerose').first()
# krankheit_therapien=session.query(Krankheit).join(Krankheit.therapien).filter(Krankheit.name=='Arteriosklerose').first()

# for therapien in krankheit_therapien:
#     print(therapien) 

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
    return result

def sqladdrelation(table1, table2, value1, value2, relation_table, kh_uok_relation=False):
    """Fügt in relation_table im Column table1_id und table2_id die jeweiligen ids ein
    kh_uok_relation True: Verbindung von Krankheiten -> uok"""
    kh_uok_string=''
    if kh_uok_relation is True:
        kh_uok_string='_kh'
    id1=sqlGetid(table1, value1)
    id2=sqlGetid(table2, value2)
    query="INSERT INTO %s (%s_id, %s_id%s) VALUES ('%s', '%s')"%(relation_table, table1, table2, kh_uok_string, id1, id2)
    sqladd(query)   

def sqlselectAll(query):
    """Query like: 'SELECT column FROM table INNER JOIN table.column WHERE condition'
    returns with fetchall() 
    """
    querytext=text(query)
    result=connection.execute(querytext).fetchall()
    list_result=[]
    for row in result:
        (element,) = row
        list_result.append(element)
    return list_result

def sqlselectOne(query):
    """Query like: 'SELECT column FROM table INNER JOIN table.column WHERE condition'
    returns with fetchone()
    """
    querytext=text(query)
    (result,)=connection.execute(querytext).fetchone()
    return result

# def krankheit_getSchemacontent(schema_name, krankheit_name, where=''):
#     "where like: 'WHERE krankheiten.name='Arteriosklerose''"
#     query=("SELECT %s.name FROM krankheiten INNER JOIN %s %s"%(schema_name, schema_name, where))
#     result=sqlselectAll(query)
#     return result