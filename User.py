import pickle
from Room import Room
import random


class Client(object):
    def __init__(self, UserID, conn, database, users, rooms):
        self._userid = UserID
        self.conn = conn
        self.db = database
        self.Users = users
        self.Rooms = rooms
        self.room = None
        self.spectating  = False
        self.playing = False

    def start(self):
        LOGOUT = False
        friends = self.db.get_friends_list(self._userid)
        friends_requests = self.db.get_friends_request_list(self._userid)
        friends_rejected = self.db.get_friends_rejected_list(self._userid)
        online_friends = self.get_online_friends(friends)
        busy_friends = self.get_busy_friends(online_friends)
        online_rooms = self.get_online_rooms(friends)
        data = {
            'ID': 10,
            'Friends': friends,
            'Friends_Requests': friends_requests,
            'Friends_Rejected': friends_rejected,
            'Online_Friends': online_friends,
            'Busy_Friends': list(busy_friends),
            'Rooms': online_rooms
        }
        sdata = pickle.dumps(data)
        self.conn.send(sdata)
        while not LOGOUT:
            rec = self.conn.recv(4096)
            data = pickle.loads(rec)
            id = data['ID']
            if id == 20:                #sending requst to the friend with friendid for playing
                friendId = data['FriendID']
                for u in self.Users:
                    if friendId == u['UserID']:
                        client = u['Client']
                        break
                    else:
                        continue
                req = {
                    'ID' : 45,
                    'Sender': self._userid,
                    'Reciever': friendId,
                    'Message': 'Friend request from user to play chess'
                }
                reqdata = pickle.dumps(req)
                client.send_friend_request(reqdata)
            elif id == 25:              ##Sending friend request status => request accept or reject normal request
                uid = data['UserID']
                fid = data['FriendID']
                if self.db.add_new_friend_request(uid, fid):
                    res = {
                        'ID': 25,
                        'Message': 'Request added successfully'
                    }
                else:
                    res = {
                        'ID': 7,
                        'Message': "Error While processing data" 
                    }
                res = pickle.dumps(res)
                self.conn.send(res)
            
            elif id == 25:                  ##Accept or reject the friend request
                fid = data['FriendID']


            elif id == 30:              ## Sending chat messages includes self uid room_id
                self.room.chat_messages.append(data)
                # continue

            elif id == 35:              ## Sending spectete message includes self uid room_id
                roomid = data['RoomID']
                if self.room == None:
                    for room in self.Rooms:
                        if roomid == room['RoomID']:
                            self.room = room['Room']
                            break
                    newuser = {
                        'UserID': self._userid,
                        'conn' : self.conn,
                    }
                    self.room.spectators.append(newuser)
                    self.spectating = True
                    res = {
                        'ID': 35,
                        'Message': "You have been added to the spectators list"
                    }
                else:
                    
                    res = {
                        'ID': 7,
                        'Message': "Room with given ID does not exist" 
                    }
                res = pickle.dumps(res)
                self.conn.send(res)    

            elif id == 40:              ## Get user profile
                profile = self.db.get_profile(self._userid)
                res = {
                    'ID': 40,
                    'Profile': profile,
                    'Message': 'User Profile'
                }
                res = pickle.dumps(res)
                self.conn.send(res)
            
            elif id == 45:              ## Friend request from friend to play chess
                req = {
                    'ID': 50,
                    'Sender': data['Sender'],
                    'Message': 'Friend request from {}'.format(data['Sender'])
                }
                reqdata = pickle.dumps(req)
                self.conn.send(reqdata)
            
            elif id == 55:              ## Game play request accept or reject
                status = data['Status']
                if status == 'Accepted':
                    roomid = self.generate_roomid()
                    self.playing = True
                    user1 = {
                        'UserID': self._userid,
                        'Conn': self.conn
                    }
                    
                    
                    for client in self.Users:
                        if data['UserID'] == client['UserID']:
                            c = client
                            break
                    clientconn = c['conn']
                    user2 = {
                        'UserID': c['UserID'],
                        'Conn': c['conn']
                    }
                    playroom = Room(roomid, user1, user2, [], db = self.db, rooms=self.Rooms)
                    rec = {
                        'ID' : 20
                        'Sender' : data['UserID'],
                        'Reciever': self._userid,
                        'Message': "Friend request accepted",
                        'Status': status,
                        'RoomID': roomid,
                        'Room' : playroom
                    }
                    clientconn.send(pickel.dumps(rec))
                    newroom = {
                        'Room': playroom,
                        'RoomID': roomid,
                    }
                    self.Rooms.append(newroom)
                    playroom.start()
                    self.room = playroom
                else :
                    rec = {
                        'ID' : 20
                        'Sender' : data['FriendID'],
                        'Reciever': self._userid,
                        'Message': "Friend request rejected",
                        'Status': status
                    }
                srec = pickle.dumps(rec)
                self.conn.send(srec)
                # continue
            elif id == 60:                          ##Board messages
                self.room.board_messaes.append(data)
            elif id == 65:                          #LOGOUT
                if self.playing:
                    res = {
                        'ID': 7,
                        'Message': "You cannot logout while playing" 
                    }
                elif self.spectating:
                    newuser = {
                        'UserID': self._userid,
                        'conn' : self.conn,
                    }
                    try:
                        self.room.spectators.remove(newuser)
                    except:
                        print("Error while removing spectator from list")
                LOGOUT = True


            else:
                print("Data : {}".formta(data))
                continue



    def get_online_friends(self, friends):      ## get the list of friends who are the friends of user and are online
        data = []
        for user in self.Users:
            if user['UserID'] in friends:
                data.append(user['UserID'])
            else:
                continue
        return data

    def get_busy_friends(self, friends):           ##Get list of friends who are playing with others
        data = []
        for room in self.Rooms:
            if room['User1'] in friends:
                data.append(room['User1'])
            elif room['User2'] in friends:
                data.append(room['User2'])
            else:
                continue
        return set(data)

    def generate_roomid(self):
        id = ['C', 'h', 'e', 's', 's', '-']
        for i in range(4):
            num = random.randint(0, 9)
            id.append(str(num))
        roomid = ''.join(id)
        if self.db.existance_of_roomid(roomid):
            return roomid
        else:
            self.generate_roomid()