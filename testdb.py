import mysql.connector
from mysql.connector import errorcode
try:
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "superuser",
        password = "Akash@2918",
        database = 'testdb',
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with username or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
cursor = mydb.cursor()
query2 = ('insert into Clients (UserID, Email, PASSWD, STATUS) values (%s, %s, %s, %s)')

def insert_data(userid, email, passwd, status='Not Verified'):
    cursor.execute(query2, (userid, email, passwd, status,))


#query = ("select * from Clients")
query = ('select * from Clients')
custquery = ("CREATE TABLE customers (name VARCHAR(255), address(255))")
print(mydb)



cursor.execute(query)
print("The type of cursor is {}".format(type(cursor)))
for data in cursor:
    print(data)

# print("Creating new table")

cursor.close()
