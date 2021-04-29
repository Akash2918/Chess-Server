import pickle
#from Room import Room
from NewRoom import Room
import time
import random
import threading
import sys

class Client(object):
    def __init__(self, UserID, conn, database, users, rooms, quickplay, message_queue):
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
        self.quickplay = quickplay
        self.message_queue = message_queue
        self.request = False
        self.cancel = False
        self.thread = None
        self.timeout = False
        self.friends = None

    def start(self):
        LOGOUT = False
        friends = self.db.get_friends_list(self._userid)
        self.friends = friends
        friends_requests = self.db.get_friends_request_list(self._userid)
        friends_rejected = self.db.get_friends_rejected_list(self._userid)
        online_friends = self.get_online_friends(friends, True)
        busy_friends = self.get_busy_friends(online_friends)
        online_rooms = self.get_online_rooms(friends)
        data = {
            'ID': 10,
            'Friends': friends,
            'Friend_Requests': friends_requests,
            'Friends_Rejected': friends_rejected,
            'Online_Friends': online_friends,
            'Busy_Friends': list(busy_friends),
            'Rooms': list(online_rooms)
        }
        sdata = pickle.dumps(data)
        self.conn.send(sdata)
        while not LOGOUT:
            try:
                rec = self.conn.recv(2048)
                if rec :
                    data = pickle.loads(rec)
                    print("The test data ", data)
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
                            for usr in self.Users:
                                if usr['UserID'] == fid:
                                    fconn = usr['conn']
                                    fdata = {
                                        'ID':27,                    ##Send online friend request
                                        'UserID':fid,
                                        'FriendID':uid,
                                        'Message':"Friend request sent by friend"
                                    }
                                    fdata = pickle.dumps(fdata)
                                    fconn.send(fdata)
                                    break
                                else:
                                    continue
                            
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

                    elif id == 28:              #delete friend from friend list
                        friendID = data['FriendID']
                        if self.db.remove_friend_from_friendlist(self._userid, friendID):
                            data = {
                                'ID':28,
                                'UserID':self._userid,
                                'FriendID':friendID,
                                'Message':'Friend deleted from friend list'
                            }
                        else:
                            data = {
                                'ID' : 7,
                                'Message': "Error while deleting friend"
                            }
                        data = pickle.dumps(data)
                        self.conn.send(data)


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
                        #chatroom.chat_messages.append(data)
                        chatroom.board_messages.append(data)
                        #chatroom.board_messages.append(data)
                        # continue
                    
                    elif id == 31:
                        print("Board message recieved")
                        print(data)
                        room = data['RoomID']
                        boardroom = None
                        for broom in self.Rooms:
                            if broom['RoomID'] == room:
                                boardroom = broom['Room']
                                break
                        boardroom.board_messages.append(data)

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
                            data = pickle.dumps(res)
                            self.conn.send(data)
                            move_log = self.room.read_from_file()
                            res = {
                                'ID': 450,
                                'MoveLog': move_log
                            }
                            data = pickle.dumps(res)
                            self.conn.send(data)
                        else:
                            
                            res = {
                                'ID': 7,
                                'Message': "Room with given ID does not exist" 
                            }
                            res = pickle.dumps(res)
                            self.conn.send(res)    

                    elif id == 40:              ## Get user profile
                        profile = self.db.get_profile(self._userid)
                        email = self.db.get_emailid(self._userid)[0]
                        res = {
                            'ID': 40,
                            #'Profile': profile,
                            'UserID':profile[0][0],
                            'Matches_Played':profile[0][2],
                            'Matches_Won':profile[0][3],
                            'Matches_Lost':profile[0][2] - profile[0][3],
                            'Points':profile[0][4],
                            'Email':email,
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
                                'Sender' : data['FriendID'],
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
                            c['Client'].room = playroom
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
                    elif id == 56:                          ###Quick play message
                        # self.quickplay.append({'UserID':self._userid, 'conn':self.conn})
                        # self.thread = threading.Thread(target=self.get_opponent)
                        # self.thread.start()
                        # while not self.cancel:
                        #     if self.request:
                        #         self.thread.join()
                        #         break
                        #     else:
                        #         continue
                        self.message_queue.append({"UserID":self._userid, 'conn':self.conn})
                        self.cancel = False
                        self.thread = threading.Thread(target=self.get_connections)
                        self.thread.start()
                        print("Thread started for getting connections")
                    elif id == 58:                  ##Quick play room creating
                        uid = data['UserID']
                        fid = data['FriendID']
                        for usr in self.Users:
                            if usr['UserID'] == fid:
                                c = usr
                                break
                        c['Client'].playing = True
                        self.playing = True
                        roomid = self.generate_roomid()
                        user1 = {
                            'Conn':self.conn,
                            'UserID':self._userid
                        }
                        user2 = {
                            'Conn' : c['conn'],
                            'UserID' : fid,
                        }
                        
                        playroom = Room(roomid=roomid, user1=user1, user2=user2, db = self.db, rooms=self.Rooms)
                        self.room = playroom
                        c['Client'].room = playroom
                        aroom = {
                            'Room':playroom,
                            'RoomID':roomid
                        }
                        self.send_busy_message()
                        c['Client'].send_busy_message()
                        self.Rooms.append(aroom)
                        self.room.start()

                    elif id == 59:
                        self.cancel = True
                        self.timeout = True
                        #self.quickplay.remove({'UserID':self._userid, 'conn':self.conn})
                        try:
                            self.thread.join()
                        except:
                            pass

                    elif id == 60:                          ##Board messages
                        self.room.board_messages.append(data)
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
                        print("Thread joined and logout successful")
                        LOGOUT = True
                        sys.exit()
                    
                    elif id == 70:
                        print("Keep Alive message From {}".format(self._userid))

                    else:
                        print("Data : {}".format(data))
                        continue
                else:
                    continue
            except (ConnectionResetError, KeyboardInterrupt, BrokenPipeError):
                return
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
    
    def send_busy_message(self):
        for usr in self.Users:
            if usr['UserID'] in self.friends:
                data = {
                    'ID':13,
                    'UserID': usr['UserID'],
                    'FriendID':self._userid,
                    'Message': "Friend is busy"
                }
                conn = usr['conn']
                rev = pickle.dumps(data)
                conn.send(rev)
            else:
                continue
        return


    # def get_opponent(self):
    #     print("Inside get_opponent")
    #     print(self.lock, self._userid)
    #     # while self.lock:
    #     #     if self.request:
    #     #         return
    #     #     else:
    #     #         continue
    #     self.lock = True
    #     print(self.quickplay)
    #     self.quickplay.remove({'UserID':self._userid, 'conn': self.conn})
    #     self.timeout = False
    #     while not self.timeout:
    #         if len(self.quickplay) > 1:
    #             opponent = self.quickplay.pop()
    #             self.lock = False
    #             print(self.quickplay)
    #             opp_uid = opponent['UserID']
    #             for usr in self.Users:
    #                 if usr['UserID'] == opp_uid:
    #                     opp_usr = usr
    #                     break
    #             if opp_usr:
    #                 opp_client = opp_usr['Client']
    #                 opp_client.request = True
    #             data = {
    #                 'ID':56,
    #                 'FriendID': opp_uid,
    #                 'UserID': self._userid,
    #                 'Message': "Quick play request matched with given friendid"
    #             }
    #             rev = pickle.dumps(data)
    #             self.conn.send(rev)
    #             opp_conn = opponent['conn']
    #             data = {
    #                 'ID':57,
    #                 'FriendID':self._userid,
    #                 'UserID':opp_uid,
    #                 'Message':"Quick play request matched with given FriendID wait for 2200"
    #             }
    #             rev = pickle.dumps(data)
    #             opp_conn.send(rev)
    #         else :
    #             continue
    #     # data = {
    #     #     'ID':400,
    #     #     'UserID':self._userid,
    #     #     'Message': 'Opponent not exist'
    #     # }
    #     #rev = pickle.dumps(data)
    #     #self.conn.send(rev)
    #     self.cancel = True
    #     #self.quickplay.remove({'UserID':self._userid, 'conn': self.conn})
    #     self.cancel = True
    #     return

    def get_connections(self):
        while not self.cancel:
            if len(self.quickplay) >=2:
                opponent = self.quickplay.pop()
                player = self.quickplay.pop()
                print("Player {} and opponent = {}".format(player, opponent))
                data1 = {
                    'ID':56,
                    'UserID':self._userid,
                    'FriendID':opponent['UserID'],
                    'Message':"Quick play request matched with given friendID"
                }
                data2 = {
                    'ID':57,
                    'UserID':opponent['UserID'],
                    'FriendID':self._userid,
                    'Message':"Quick play request matched with given friendID wait for 2200 message"
                }
                rec1 = pickle.dumps(data1)
                rec2 = pickle.dumps(data2)
                self.conn.send(rec1)
                opponent['conn'].send(rec2)
                print("Opponent messages sent ")
                self.cancel = False
            elif len(self.message_queue):
                message = self.message_queue.pop()
                self.quickplay.append(message)
                print("New request recieved")
            
        return