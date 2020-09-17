import psycopg2

con=psycopg2.connect(database='Lernprogramm DB', user='Owner', password='Ownerpassword')
cur=con.cursor()

# #INSERT
# query="""INSERT INTO Accounts VALUES(7,'bla','passwort');"""
# cur.execute(query)

# con.commit()

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

cur.close()
con.close()






