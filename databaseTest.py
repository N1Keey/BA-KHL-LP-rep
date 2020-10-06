import psycopg2
import database

con=psycopg2.connect(database='Lernprogramm DB', user='Owner', password='Ownerpassword')
cur=con.cursor()

# userids=database.readAccounts()
# for userid in userids:
#     print(userid)

# lastuserdata=database.readsql("Accounts")[-1]
# lastuserid=lastuserdata[0]
# print(lastuserid)


#CREATE TABLE
# queryct="""CREATE TABLE Krankheiten(
#     name TEXT,
#     PRIMARY KEY(name)
#     );"""
# cur.execute(queryct)

# #INSERT
# query="""INSERT INTO Accounts VALUES(7,'bla','passwort');"""
# cur.execute(query)
# con.commit()

database.writesql("Accounts","0,'Nschick@mail.hs-ulm.de','1qay2wsx3edc','Owner'")

# # DELETE
# cur.execute('DELETE FROM Accounts')
# con.commit()
select_query="SELECT * FROM Accounts"
cur.execute(select_query)
accountdata=cur.fetchall()
for row in accountdata:
    print('Id = ', row[0])
    print('Email = ', row[1])
    print('Passwort = ', row[2])
    print('Status = ', row[3])

# email='Nschick@mail.hs-ulm.de'
# dbemails=database.readsql('accounts','email')
# if email in dbemails:
#     pw_val='Email existiert schon!'
# else:
#     pw_val='Email existiert noch nicht!'
# print(pw_val)
database.close()







