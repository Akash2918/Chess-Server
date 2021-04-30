import threading
import pickle
import random


class Room(object):
    def __init__(self, roomid, user1, user2, db, rooms):
        self.RoomID = roomid
        self.User1 = user1['UserID']
        self.User2 = user2['UserID']
        self.conn1 = user1['Conn']
        self.conn2 = user2['Conn']
        self.db = db
        self.Rooms = rooms
        self.spectators = [{'UserID':self.User1, 'conn':self.conn1}, {'UserID':self.User2, 'conn': self.conn2}]
        self.board_messages = []
        self.win = None
        self.lost = None
        self.game_end = False
        self.thread = threading.Thread(target=self.broadcast_messages)
        with open('./Rooms/{}.csv'.format(self.RoomID), 'a') as f:
            pass                                       ##Update it
        self.moveno = None
        self.move = None
        self.white = None
        self.black = None
        self.lost = None
        self.win = None
        
        
    def update_database(self, message):
        self.move_log = b'000000'#self.read_move_log()
        self.db.insert_History_details(self.RoomID, self.move_log)
        self.db.update_lost_user_points(self.lost, message)
        #self.db.update_lost_status(self.lost)

        print("Data added to the database successfully")


        return 

    def read_move_log(self):
        with open('./Rooms/{}.csv'.format(self.RoomID), 'rb') as fdata:
            rdata = fdata.read()
        
        return rdata

    def set_turns(self):
        num = random.randint(1, 100)
        if num%2 == 0:
            data1 = {
                'ID': 2200,
                'Turn': 'White',
                'Message': 'Start game with white pieces',
                'RoomID': self.RoomID
            }
            self.white = [self.User1, 'White']
            data2 = {
                'ID': 2200,
                'Turn': 'Black',
                'Message': 'Start game with black pieces',
                'RoomID': self.RoomID
            }
            self.black = [self.User2, 'Black']
        else:
            self.white = [self.User2, 'White']
            data2 = {
                'ID': 2200,
                'Turn': 'White',
                'Message': 'Start game with white pieces',
                'RoomID': self.RoomID
            }
            self.black = [self.User1, 'Black']
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
        with open('./Rooms/{}.csv'.format(self.RoomID), 'a') as fdata:
            fdata.write("UserID\tColor\n")
            fdata.write("{}\t{}\n".format(self.black[0],self.black[1]))
            fdata.write("{}\t{}\n".format(self.white[0],self.white[1]))
        print("Turns are set")
        return
    
    def write_to_file(self, moveno, uid, start, stop):
        with open('./Rooms/{}.csv'.format(self.RoomID), 'a') as fdata:
            fdata.write('{}\t{}\t{}\t{}\n'.format(moveno, uid, start, stop))
        return

    def read_from_file(self,):
        with open("./Rooms/{}.csv".format(self.RoomID), 'r') as fdata:
            data = fdata.read()
        return data

    def broadcast_messages(self):
        with open('./Rooms/{}.csv'.format(self.RoomID), 'a') as fdata:
            fdata.write("Moveno\tUserID\tStart\tStop\n")
        while not self.game_end:
            if len(self.board_messages) > 0:
                print("The messages list contain {}".format(self.board_messages))
                message = self.board_messages.pop()
                print(message)
                uid = message['UserID']
                if message['ID'] == 60:
                    if message['Checkmate'] or message['Stalemate'] or message['Forfeit'] or message['Left']:
                        self.lost = uid
                        if uid == self.User1:
                            self.win = self.User2
                        else:
                            self.win  = self.User1
                        self.game_end = True
                    moveno = message['MoveNo']
                    start = message['Start']
                    stop = message['Stop']
                    self.write_to_file(moveno, uid, start, stop)
                    print("Written to file")

                data = pickle.dumps(message)
                for user in self.spectators:
                    if user['UserID'] == uid:
                        continue
                    else:
                        conn = user['conn']
                        conn.send(data)
                        #print("Message sent to uid {}".format(user['UserID']))
                #print("Message with {} uid sent to all users".format(uid))
            else:
                continue
        self.update_database(message)
        print("All messages sent")
        return


    def start(self):
        print("Room is started ")
        print("User 1 {}".format(self.User1))
        print("User 2 {}".format(self.User2))
        print("conn 1 {}".format(self.conn1))
        print("conn 2 {}".format(self.conn2))
        self.set_turns()
        self.thread.start()
        print("Returning from start")
        return

    


