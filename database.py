from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql+psycopg2://Owner:Ownerpassword@localhost/Lernprogramm_DB")
connection=engine.connect()
Base=declarative_base()
Session = sessionmaker(bind=engine)
session=Session()

class User(Base):
    __tablename__='users'

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(255))
    roles = relationship('Role', secondary='users2roles')

class Role(Base):
    __tablename__='roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True)
    description = Column(String(255))

class User2Role(Base):
    __tablename__='users2roles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'))

Base.metadata.create_all(engine)

#USER functions
def user_regist(user_email, user_password):
    """Adds User to Database and gives the standard-role: 'User'
    """
    new_User=User(email=user_email, password=user_password)
    new_user_role=session.query(Role).filter(Role.name=='User').first()
    new_User.roles=[new_user_role]
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
            
def user_getall():
    user_list=[]
    users=session.query(User).join(User.roles).all()
    for user in users:
        role_list=[]
        for role in user.roles:
            role_list.append(role.name)
        user_list.append('ID: %s,Email: %s, Password: %s, Roles: %s'%(user.id, user.email, user.password, role_list))
    return user_list

#ROLE functions
def role_add(role_name, role_description):
    "Adds Role to Database"
    new_Role=Role(name=role_name, description=role_description)
    session.add(new_Role)
    session.commit()

# admin_user=session.query(User).filter(User.email=='Nschick@mail.hs-ulm.de').first()
# admin_role=session.query(Role).filter(Role.name=='Admin').first()
# user_role=session.query(Role).filter(Role.name=='User').first()
# admin_user.roles=[admin_role,user_role]
# for role in admin_user.roles:
#     print('ID: %s,Email: %s, Password: %s, Roles: %s'%(admin_user.id, admin_user.email, admin_user.password, role.name))
# session.commit()

# users=session.query(User).join(User.roles).all()
# role_add('Admin','Role for managing the User-Registration and the distribiution of the Roles')

# for user in users:
#     for role in user.roles:
#         print('ID: %s,Email: %s, Password: %s, Roles: %s'%(user.id, user.email, user.password, role.name))

# roles=session.query(Role).all()
# for role in roles:
#     print('Name: %s, Description: %s'%(role.name, role.description))
print(user_getall())
