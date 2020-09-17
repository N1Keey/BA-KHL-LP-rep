import psycopg2

# Postgresql
#opens connection and cursor
con=psycopg2.connect(database="Lernprogramm DB", user="Owner", password="Ownerpassword")
cur=con.cursor()

#writes query and executes it
def writesql(table,columns,data):
    query = "INSERT INTO %s VALUES(%s)"%(table,data)
    cur.execute(query)     

def readsql(table,columns,limit=None):
    query = "SELECT * FROM %s;"%(table)
    cur.execute(query)
    # fetch data
    userdata = cur.fetchall()
    return userdata[len(userdata)-limit if limit else 0:]

#commits changes, closes cursor and connection
def close():
    con.commit()
    cur.close()
    con.close() 

#Account    
#insert Register info into Accounts Table
def getLastuserid():
    userdata=readsql("Accounts","userid")
    lastuserdata=userdata[-1]
    lastuserid=lastuserdata[0]
    return lastuserid

def accRegister(email,password):
    userid=getLastuserid()+1
    writesql("Accounts","'userid','email','passwort'","%d, '%s', '%s'"%(userid,email,password))
    close()

def accLogin(email,password):
    accounts=readsql("Accounts","'email','passwort'")
    emailexist=False
    for account in accounts:
        if email in account:
            emailexist=True
            if account[2]==password:
                return 'Login erfolgreich!'
            else:
                return 'Passwort falsch!'
    if emailexist is False:
        return 'Email falsch!'

lastuserid=getLastuserid()
print(lastuserid)


#Krankheiten