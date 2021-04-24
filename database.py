import mysql.connector
from mysql.connector import errorcode
try:
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "superuser",
        password = "Akash@2918",
        database = 'chessdb',
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
        self._add_new_user_query = ("insert into Clients (UserID, Email, PASSWD, STATUS) values (%s, %s, %s, %s)")
        self._verify_user_query = ("update Clients set STATUS = %s where UserID = %s")
        self._unique_email_query = ("select * from Clients where Email = %s")
        self._get_friends_list_query = ("select FriendID from Friends where UserID = %s and STATUS = 'Accepted'")
        self._get_friends_list2_query = ("select UserID from Friends where FriendID = %s and STATUS = 'Accepted'")
        self._add_new_friend_request_query = ("insert into Friends (UserID, FriendID, STATUS) values (%s, %s, %s)")
        self._get_user_profile_query = ("select * from Profile where UserID = %s")
        self._get_friends_rejected_list_query = ("select FriendID from Friends where UserID = %s and STATUS = 'Rejected'")
        self._get_friends_request_list_query = ("select UserID from Friends where UserID = %s and STATUS = 'Requested'")
        self._update_profile_query = ("update Profile set Profile_Image = %s where UserID = %s")
        self._update_password_query = ("update Clients set PASSWD = %s where UserID = %s")
        self._existance_email_query = ("select * from Clients where Email = %s")
        self._existance_roomid_query = ("select RoomID from Games where RoomID = %s")
        self._insert_roomid_todb_query = ("insert into Games (RoomID, Player1, Player2) values (%s, %s, %s)")
        self._insert_to_history_query = ("insert into History (RoomID, currentDate, Move_Logs) values (%s, NOW(), %s)")
        self._update_win_status_query = ("update Profile set Matches_Played = Matches_Played + 1, Matches_Won = Matches_Won + 1 where UserID = %s")
        self._update_lost_status_query = ("update Profile set Matches_Played = Matches_Played + 1 where UserID = %s")
        self._update_friends_accept_query = ("update Friends set STATUS = %s where UserID = %s and FriendID = %s")
        self._existance_friend_query = ("select UserID from Clients where UserID = %s")
        self._existance_of_friend_query = ("select * from Friends where UserID = %s and FriendID = %s")          
        self._delete_friend_query = ("delete from Friends where UserID = %s and FriendID = %s")

    def update_user_profile(self, uid, data):
        try:
            self.cursor.execute(self._update_profile_query, (data['Image'], uid, ))
            mydb.commit()
            return True
        except:
            return False
    
    def remove_friend_from_friendlist(self, uid, fid):
        data = []
        self.cursor.execute(self._existance_of_friend_query, (uid, fid, ))
        for row in self.cursor:
            data.append(row)
        if data :
            self.cursor.execute(self._delete_friend_query, (uid, fid, ))
            mydb.commit()
        else:
            self.cursor.execute(self._existance_of_friend_query, (fid, uid,))
            for row in self.cursor:
                data.append(row)
            if data:
                self.cursor.execute(self._delete_friend_query, (fid, uid, ))
                print("friend with id = {} deleted".format(fid))
                mydb.commit()
                return True
        return True


    def update_win_status(self, uid):
        try:
            self.cursor.execute(self._update_win_status_query, (uid, ))
            mydb.commit()
            return True
        except:
            print("Error while updating win status")
            return False

    def add_friends_request_status(self, data):
        uid = data['UserID']
        fid = data['FriendID']
        status = data['Status']
        try:
            self.cursor.execute(self._update_friends_accept_query, (status, fid, uid))
            mydb.commit()
            return True
        except:
            return False

    def update_lost_status(self, uid):
        try:
            self.cursor.execute(self._update_lost_status_query, (uid, ))
            mydb.commit()
            return True
        except:
            print("Error while updating lost status")
            return False

    def verify_user(self, uid):
        try:
            self.cursor.execute(self._verify_user_query, ("Verified", uid, ))
            mydb.commit()
            return True
        except:
            print("Error while varifing user")
            return False

    def update_user_password(self, uid, password):
        try:
            self.cursor.execute(self._update_password_query, (password, uid, ))
            mydb.commit()
            return True
        except:
            return False
        
    def existance_of_user(self, uid, email):
        try:
            self.cursor.execute(self._existance_email_query, (email, ))
            data = []
            for d in self.cursor:
                data.append(d)
            print(data)
            qemail = data[0][1]
            if qemail == email:
                 return True
            else:
                return False
        except:
            print("Error while processing email query")
            return False

    def existance_of_roomid(self, roomid):
        self.cursor.execute(self._existance_roomid_query, (roomid, ))
        data = []
        for room in self.cursor:
            data.append(room)
        return True if len(data) == 0 else False

    def insert_game_details(self, roomid, player1, player2):
        try:
            self.cursor.execute(self._insert_roomid_todb_query, (roomid, player1, player2, ))
            mydb.commit()
            return True
        except:
            return False
        
    def insert_History_details(self, roomid, move_log):
        try:
            self.cursor.execute(self._insert_to_history_query, (roomid, movelog, ))
            mydb.commit()
            return True
        except:
            print("Error while inserting molog to database")
            return False

    def validate_user(self, userid, password):
        self._uid, self._password = userid, password
        self.cursor.execute(self._validate_user_query, (self._uid, self._password,))
        users = []
        for data in self.cursor:
            #print(data)
            users.append(data)
        return True if len(users) == 1 else False
    
    def Add_new_User(self, UserID, Email, Password):
        #self._uid, self._email,  self._password = UserID, Email, Password
        self.cursor.execute(self._unique_email_query, (Email, ))
        data = []
        for email in self.cursor:
            data.append(email)
        if len(data) == 0:
            self.cursor.execute(self._add_new_user_query, (UserID, Email, Password, "NOT Verified", ))
            mydb.commit()
            return True
        else:
            return False

    def get_friends_list(self, uid):
        self._uid = uid
        self.cursor.execute(self._get_friends_list_query, (self._uid, ))
        data = []
        for friend in self.cursor:
            data.append(friend[0])
        self.cursor.execute(self._get_friends_list2_query, (self._uid, ))
        for friend in self.cursor:
            data.append(friend[0])
        return data

    def get_friends_request_list(self, uid):
        #try:
        self.cursor.execute(self._get_friends_request_list_query, (uid, ))
        friends = []
        for friend in self.cursor:
            friends.append(friend)
        return friends
        # except:
        #     print("Error occured while processing friend request query")
        #     return []

    def get_profile(self, uid):
        profile = []
        self.cursor.execute(self._get_user_profile_query, (uid, ))
        for p in self.cursor:
            profile.append(p)

        print("Profile of {} user is {}".format(uid, profile))
        return profile
    
    def get_friends_rejected_list(self, uid):
        self.cursor.execute(self._get_friends_rejected_list_query, (uid, ))
        friends = []
        for friend in self.cursor:
            friends.append(friend)
        # print("The friends list is {}".format(friends))
        return friends

    def add_new_friend_request(self, userid, friendid):
        try:
            self.cursor.execute(self._add_new_friend_request_query, (userid, friendid, 'Pending'))
            mydb.commit()
            return True
        except:
            print("Error while inserting data into database")
            return False
        
    def check_existance_of_user(self, fid):
        self.cursor.execute(self._existance_friend_query, (fid, ))
        data = []
        for fid in self.cursor:
            data.append(fid)
        udata = []
        for u in data[0]:
            udata.append(u)
        return udata 

# query = ("select * from Clients")
# custquery = ("CREATE TABLE customers (name VARCHAR(255), address(255))")
# print(mydb)


# cursor.execute(query)
# print("The type of cursor is {}".format(type(cursor)))
# for data in cursor:
#     print(data)

# # print("Creating new table")

# cursor.close()
