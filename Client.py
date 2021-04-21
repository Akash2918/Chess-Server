import socket 
import threading
import pickle

class User(object):
    def __init__(self):
        self.sending_messages = []
        self.recieving_messages = []
        self.userid = None
        self.password = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("", 12000))
        self.recieve_thread = 
        self.send_thread = 
        self.logout = False

    
    def recieve_messages(self):
        while not self.logout:
            message = self.sock.recv(4096) 
            data = pickle.loads(message)
            self.recieving_messages.append(data)
        return

    def send_messages(self):
        while not self.logout:
            if len(self.sending_messages) > 0:
                message = self.sending_messages.pop(0)
                data = pickle.dumps()
                self.sock.send(data)
            else:
                continue
        return