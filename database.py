import psycopg2

# Postgresql
#opens connection and cursor
con=psycopg2.connect(database="Lernprogramm DB", user="Owner", password="Ownerpassword")
cur=con.cursor()

#writes into table, data
def writesql(table,data):
    query = "INSERT INTO %s VALUES(%s)"%(table,data)
    cur.execute(query)     
    con.commit()

#reads data from given table
def readsql(table,limit=None):
    query = "SELECT * FROM %s;"%(table)
    cur.execute(query)
    # fetches all data
    userdata = cur.fetchall()
    return userdata[len(userdata)-limit if limit else 0:]

#commits changes, closes cursor and connection
def close():
    con.commit()
    cur.close()
    con.close() 

#Account         
def readAccounts(column=None):
    """Alle Daten: column=leer
    ID's: column=0
    Emails: column=1
    Passwörter: column=2
    status: column=3
    """
    output=[]
    accountsdata=readsql("Accounts")
    if column==None:
        output=accountsdata
    else:
        for data in accountsdata:
            prefdata=data[column]
            output.append(prefdata)
    return output
        

#gives you the id of the last registered user
def getLastuserid():
    userids=readAccounts(column=0)
    lastuserid=userids[-1]
    return lastuserid

#Registers Account with given email and password
def accRegister(email,password):
    #for an ascending order of ids
    status='User'
    userid=getLastuserid()+1
    if userid==None:
        userid=0
    writesql("Accounts","%d, '%s', '%s','%s'"%(userid,email,password,status))

#sign up, if your account exists and the required password is correct
def accLogin(email,password):
    accounts=readAccounts()
    #checks if email is in database
    for account in accounts:
        if email == account[1]:
            #account[0]= id, account[1]=email, account[2]=password
            if account[2]==password:
                return True
            else:
                return False

#Krankheiten