import random
import pickle

class Room(object):
    def __init__(self, roomid=None, user1=None, user2=None, spectators= [], db=None, rooms=None):
        self.RoomID = roomid
        self.User1 = user1['UserID']          ##User is a dictonary containing userid, conn
        self.User2 = user2['UserID']
        self.Rooms = rooms
        self.spectators = spectators        ## Spectators is list of user dict containing uuid and conn
        self.board_messaes = []
        self.db = db
        self.chat_messages = []
        self.game_end = False
        self.conn1 = user1['Conn']
        self.conn2 = user2['Conn']
        self.win = None
        self.lost = None
        self.move_log = None
        self.set_turns()

    def update_database(self):
        self.db.insert_History_details(self.RoomID, self.move_log)
        self.db.update_lost_status(self.lost)
        self.db.update_win_status(self.win)
        
        print("Data added to the database successfully")


        return

    def set_turns(self):
        num = random.randint(1, 100)
        if num%2 == 0:
            data1 = {
                'ID': 2200,
                'Turn': 'White',
                'Message': 'Start game with white pieces',
                'RoomID': self.RoomID
            }
            data2 = {
                'ID': 2200,
                'Turn': 'Black',
                'Message': 'Start game with black pieces',
                'RoomID': self.RoomID
            }
            # res1 = pickle.dumps(data1)
            # res2 = pickle.dumps(data2)
            # self.conn1.send(res1)
            # self.conn2.send(res2)
        else:
            data2 = {
                'ID': 2200,
                'Turn': 'White',
                'Message': 'Start game with white pieces',
                'RoomID': self.RoomID
            }
            data1 = {
                'ID': 2200,
                'Turn': 'Black',
                'Message': 'Start game with black pieces',
                'RoomID': self.RoomID
            }

        res1 = pickle.dumps(data1)
        res2 = pickle.dumps(data2)
        self.conn1.send(res1)
        self.conn2.send(res2)

        return


    def broadcast_message(self, message):
        sender = message['Sender']
        if sender == self.User1:
            self.conn2.send(message)
            for spect in self.spectators:
                conn = spect['conn']
                conn.send(message)
        elif sender == self.User2:
            self.conn1.send(message)
            for spect in self.spectators:
                conn = spect['conn']
                conn.send(message)
        else:
            self.conn1.send(message)
            self.conn2.send(message)
            for spect in self.spectators:
                if sender == spect['UserID']:
                    continue
                else:
                    conn = spect['conn']
                    conn.send(message)
        return

    def start(self):
        while not self.game_end :
            if len(self.board_messaes) > 0:
                message = self.board_messaes.pop(0)
                checkmate = message['Checkmate']
                if checkmate:
                    self.game_end = True
                    self.win = message['Win']
                    self.lost = message['Lost']
                    self.move_log = message['Move_log']
                    self.spectators.clear()
                    i = 0
                    for i in range(len(self.Rooms)):
                        if self.Rooms[i]['RoomID'] == self.RoomID:
                            self.Rooms.pop(i)
                        else:
                            continue
                # self.broadcast_message(message)
            elif len(self.chat_messages) > 0:
                message = self.chat_messages.pop(0)
            else: 
                continue
            self.broadcast_message(message)    
        self.update_database()
        return
    # def broadcast_chat_message(self, message):
    #     pass