import psycopg2

# Postgresql
#opens connection and cursor
con=psycopg2.connect(database="Lernprogramm DB", user="Owner", password="Ownerpassword")
cur=con.cursor()

#writes into table, data
def writesql(table,data):
    query = "INSERT INTO %s VALUES(%s)"%(table,data)
    cur.execute(query)  
    close()   

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
#gives you the id of the last registered user
def getLastuserid():
    lastuserdata=readsql("Accounts")[-1]
    lastuserid=lastuserdata[0]
    return lastuserid

#Registers Account with given email and password
def accRegister(email,password):
    #for an ascending order of ids
    status='user'
    userid=getLastuserid()+1
    if userid==None:
        userid=0
    writesql("Accounts","%d, '%s', '%s','%s'"%(userid,email,password,status))

#sign up, if your account exists and the required password is correct
def accLogin(email,password):
    emails=readsql("Accounts")
    #checks if email is in database
    emailexist=False
    for account in accounts:
        if email in account:
            emailexist=True
            #account[0]= id, account[1]=email, account[2]=password
            if account[2]==password:
                return 'Login erfolgreich!'
            else:
                return 'Passwort falsch!'
    if emailexist is False:
        return 'Email falsch!'

#Krankheiten