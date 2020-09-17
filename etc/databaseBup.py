# import psycopg2

# #connect to db
# con = psycopg2.connect(
#     database="Lernprogramm DB", user="Owner", password="Ownerpassword")

# #cursor
# cur=con.cursor()

# class AccDB():
#     def __init__(self, userid, email, password):
#         self.userid=userid
#         self.email=email
#         self.password=password


#     #insert Register info into Accounts Table
#     def accRegister(self):
#         insert_query = """
#         INSERT INTO Accounts(UserID, Email, Passwort) 
#         Values (%s,%s,%s)"""
#         insert_values=(self.userid,self.email,self.password)
#         return (insert_query,insert_values)

# cur.execute(AccDB.accRegister())

# #commit
# con.commit()

# #Read Accounts
# select_query="select * from Accounts"
# cur.execute(select_query)

# accountdata=cur.fetchall()
# for row in accountdata:
#     print('Id = ', row[0])
#     print('Email = ', row[1])
#     print('Passwort = ', row[2])

# #close cursor
# cur.close()

# #close connection
# con.close()