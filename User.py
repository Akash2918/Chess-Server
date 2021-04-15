import pickle
from Room import Room


class Client(object):
    def __init__(self, UserID, conn, database, users, rooms):
        self._userid = UserID
        self.conn = conn
        self.db = database
        self.Users = users
        self.Rooms = rooms

    def start(self):
        LOGOUT = False
        friends = self.db.get_friends_list(self._userid)
        friends_requests = self.db.get_friends_request_list(self._userid)
        friends_rejected = self.db.get_friends_rejected_list(self._userid)
        online_friends = self.get_online_friends(friends)
        busy_friends = self.get_busy_friends(online_friends)
        data = {
            'ID': 10,
            'Friends': friends,
            'Friends_Requests': friends_requests,
            'Friends_Rejected': friends_rejected,
            'Online_Friends': online_friends,
            'Busy_Friends': busy_friends
        }
        sdata = pickle.dumps(data)
        self.conn.send(sdata)
        while not LOGOUT:
            rec = self.conn.recv(1024)
            data = pickle.loads(rec)
            id = data['ID']
            if id == 20:                #sending requst to the friend with friendid for playing
                friendId = data['FriendID']
                for u in self.Users:
                    if friendId == u['UserID']:
                        client = u['client']
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
                continue

            elif id == 30:              ## Sending chat messages includes self uid room_id
                continue

            elif id == 35:              ## Sending spectete message includes self uid room_id
                continue

            elif id == 40:              ## Get user profile
                continue
            
            elif id == 45:              ## Friend request from friend to play chess
                req = {
                    'ID': 50,
                    'Sender': data['Sender'],
                    'Message': 'Friend request from {}'.format(data['Sender'])
                }
                reqdata = pickle.dumps(req)
                self.conn.send(reqdata)
            
            elif id == 55:              ## Game play request accept or reject
                continue

            else:
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
