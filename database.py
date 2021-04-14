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

class Database(object):
    def __init__(self):
        self.cursor = cursor
        self._username = None
        self._password = None
        self._email = None
        self._uname = None
        self._uid = None
        
        ####### Database Queries
        self._validate_user_query = ("select * from Clients where UserID = %s and PASSWD = %s")
        self._add_new_user_query = ("insert into Clients (UserID, Email, Username, PASSWD) values (%s, %s, %s, %s)")
        self._unique_email_query = ("select * from Clients where Email = %s")

    def validate_user(self, userid, password):
        self._uid, self._password = userid, password
        self.cursor.execute(self._validate_user_query, (self._uid, self._password,))
        users = []
        for data in self.cursor:
            #print(data)
            users.append(data)
        return True if len(users) == 1 else False
    
    def Add_new_User(self, UserID, Email, Username, Password):
        self._uid, self._email, self._uname, self._password = UserID, Email, Username, Password
        self.cursor.execute(self._unique_email_query, (self._email, ))
        data = []
        for email in self.cursor:
            data.append(email)
        if len(data) == 0:
            self.cursor.execute(self._add_new_user_query, (self._uid, self._email, self._uname, self._password,))
            return True
        else:
            return False





# query = ("select * from Clients")
# custquery = ("CREATE TABLE customers (name VARCHAR(255), address(255))")
# print(mydb)


# cursor.execute(query)
# print("The type of cursor is {}".format(type(cursor)))
# for data in cursor:
#     print(data)

# # print("Creating new table")

# cursor.close()
