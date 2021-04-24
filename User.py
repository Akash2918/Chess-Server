import pickle
from Room import Room
import random
import struct
import sys

class Client(object):
    def __init__(self, UserID, conn, database, users, rooms, threads):
        self._userid = UserID
        self.conn = conn
        self.db = database
        self.Users = users
        self.Rooms = rooms
        self.room = None
        self.spectating  = False
        self.playing = False
        self.imgbuf = b''
        self.pieces = None
        self.piece_no = None
        self.threads = threads

    def start(self):
        LOGOUT = False
        friends = self.db.get_friends_list(self._userid)
        friends_requests = self.db.get_friends_request_list(self._userid)
        friends_rejected = self.db.get_friends_rejected_list(self._userid)
        online_friends = self.get_online_friends(friends, True)
        busy_friends = self.get_busy_friends(online_friends)
        online_rooms = self.get_online_rooms(friends)
        data = {
            'ID': 10,
            'Friends': friends,
            'Friends_Requests': friends_requests,
            'Friends_Rejected': friends_rejected,
            'Online_Friends': online_friends,
            'Busy_Friends': list(busy_friends),
            'Rooms': list(online_rooms)
        }
        sdata = pickle.dumps(data)
        self.conn.send(sdata)
        while not LOGOUT:
            rec = self.conn.recv(2048)
            if rec :
                data = pickle.loads(rec)
                id = data['ID']
                if id == 20:                #sending requst to the friend with friendid for playing
                    friendId = data['FriendID']
                    req = {
                            'ID' : 50,
                            'Sender': self._userid,
                            'Reciever': friendId,
                            'Message': 'Friend request from user to play chess'
                        }
                    reqdata = pickle.dumps(req)
                    for u in self.Users:
                        if friendId == u['UserID']:
                            client = u['Client']
                            cconn = u['conn']
                            cconn.send(reqdata)
                            print("Message sent")
                            break
                        else:
                            continue
                    # if client:
                    #     req = {
                    #         'ID' : 50,
                    #         'Sender': self._userid,
                    #         'Reciever': friendId,
                    #         'Message': 'Friend request from user to play chess'
                    #     }
                    #     reqdata = pickle.dumps(req)
                    #     client.conn.send(reqdata)
                    #     print("Message sent")
                    # else:
                    #     continue
                
                elif id == 24:                  ##Check existance of user
                    fid = data['FriendID']
                    data = self.db.check_existance_of_user(fid)
                    if data:
                        rev = {
                            'ID':24,
                            'Data': data,
                            'Status': True
                        }
                        self.conn.send(pickle.dumps(rev))
                    else:
                        res = {
                            'ID': 7,
                            'Message': "No user with given ID",
                            'Status': False 
                        }
                        res = pickle.dumps(res)
                        self.conn.send(res)

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
                
                elif id == 26:                  ##Accept or reject the friend request
                    fid = data['FriendID']
                    self.db.add_friends_request_status(data)

                elif id == 30:              ## Sending chat messages includes self uid room_id
                    #self.room.chat_messages.append(data)
                    #self.room.board_messaes.append(data)
                    print("The recieved mesage is {}".format(data))
                    room = data['RoomID']
                    chatroom = None
                    for croom in self.Rooms:
                        if croom['RoomID'] == room:
                            chatroom = croom['Room']
                            break
                    chatroom.chat_messages.append(data)
                    #chatroom.board_messages.append(data)
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
                
                elif id == 41:      ##Update User Profile
                    self.imgbuf += data['Image']
                    self.piece_no = data['Piece_No']
                    self.pieces = data['Pieces']
                    print("{} recieved ".format(self.piece_no))

                    # if self.db.update_user_profile(self._userid, data):
                    #     data = {
                    #         'ID':41,
                    #         'Message': 'User profile updated successfully'
                    #     }
                    # else:
                    #     data = {
                    #         'ID': 7,
                    #         'Message': 'Failed to update user profile'
                    #     }
                    # rev = pickle.dumps(data)
                    # self.conn.send(rev)
                        
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
                            if data['FriendID'] == client['UserID']:
                                c = client
                                break
                        clientconn = c['conn']
                        user2 = {
                            'UserID': c['UserID'],
                            'Conn': clientconn
                        }
                        playroom = Room(roomid, user1, user2, db = self.db, rooms=self.Rooms)
                        nrec = {
                            'ID' : 55,
                            'Sender' : data['UserID'],
                            'Reciever': self._userid,
                            'Message': "Friend request accepted",
                            'Status': status,
                            'RoomID': roomid,
                            #'Room' : playroom
                        }
                        clientconn.send(pickle.dumps(nrec))
                        newroom = {
                            'Room': playroom,
                            'RoomID': roomid,
                        }
                        self.Rooms.append(newroom)
                        self.room = playroom
                        print(bool(self.room))
                        self.room.start()
                        #playroom.start()
                        #self.room = playroom
                    else :
                        rec = {
                            'ID' : 55,
                            'Sender' : self._userid,#data['FriendID'],
                            'Reciever': data['FriendID'], #self._userid,
                            'Message': "Friend request rejected",
                            'Status': status
                        }
                    srec = pickle.dumps(rec)
                    self.conn.send(srec)
                    # continue
                elif id == 60:                          ##Board messages
                    self.room.board_messaes.append(data)
                elif id == 65:                          #LOGOUT
                    print("Recieved logout message from {}".format(self._userid))
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
                    self.get_online_friends(friends, False)
                    # for usr in self.threads:
                    #     if self.conn == usr['conn']:
                    #         thread = usr['Thread']
                    #         break
                    #thread.join()
                    print("Thread joined and logout successful")
                    LOGOUT = True
                    sys.exit()

                else:
                    print("Data : {}".formta(data))
                    continue
            else:
                continue
        return




    def get_online_friends(self, friends, flag):      ## get the list of friends who are the friends of user and are online
        data = []
        for user in self.Users:
            if user['UserID'] in friends:
                data.append(user['UserID'])
                if flag:
                    #conn = user['conn']
                    online_friend = {
                        'ID' : 11,
                        'FriendID': self._userid,
                        'UserID': user['UserID']
                    }
                    conn = user['conn']
                    conn.send(pickle.dumps(online_friend))
                else:
                    offline_friend = {
                        'ID':12,
                        'FriendID': self._userid,
                        'UserID': user['UserID'],
                        'Message': "Friend is offline"
                    }
                    conn = user['conn']
                    conn.send(pickle.dumps(offline_friend))
                
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

    def get_online_rooms(self, friends):
        rooms = []
        for room in self.Rooms:
            playroom = room['Room']
            if playroom.User1 in friends:
                data = {
                    'FriendID':playroom.User1,
                    'RoomID': room['RoomID']
                }
                rooms.append(data)
            elif playroom.User2 in friends:
                data = {
                    'FriendID':playroom.User2,
                    'RoomID': room['RoomID']
                }
                rooms.append(data)
            else:
                continue
        
        return set(rooms)
        