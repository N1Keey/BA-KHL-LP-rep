from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql+psycopg2://Owner:Ownerpassword@localhost/Lernprogramm_DB")
connection=engine.connect()
Base=declarative_base()
Session = sessionmaker(bind=engine)
session=Session()

roles_users = Table('roles_users',Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
    )

class User(Base):
    __tablename__='users'

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(255))
    roles = relationship('Role', secondary=roles_users)
    

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
    new_User.roles=[Role(name='User', description='Der normale User eben')]
    session.add(new_User)
    session.commit()

def user_login(user_email, user_password):
    """returns True if Email exists and Pw is right
    False if Email isnt existing or password isnt right
    """
    users=session.query(User)
    for user in users:
        if user_email==user.email and user_password==user.password:
            return True
        else:
            return False

def role_add(role_name, role_description):
    "Adds Role to Database"
    new_Role=Role(name=role_name, description=role_description)
    session.add(new_Role)
    session.commit()

# testusers=session.query(User).all()
# for user in testusers:
#     print('ID: %s,Email: %s, Password: %s, Roles: %s'%(user.id, user.email, user.password, user.roles))

# roles=session.query(Role).all()
# for role in roles:
#     print('Name: %s, Description: %s'%(role.name, role.description))

