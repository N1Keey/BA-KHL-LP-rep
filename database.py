from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///khl_lp.db')

connection=engine.connect()
Base=declarative_base()
Session = sessionmaker(bind=engine)
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
    users=session.query(User)
    for user in users:
        if user_email==user.email and user_password==user.password:
            return True
        else:
            return False

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

