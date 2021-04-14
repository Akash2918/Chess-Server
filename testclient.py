import socket
import pickle

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("", 12000))

user = {
    'Username': 'Akash2918',
    'Password': 'Akash@123',
}

user1 = {
    'Username': 'Rutvik123',
    'Password': 'Rutvik@123',
}

data = pickle.dumps(user1)
print("The length of data is {}".format(len(data)))
sock.send(data)

print("Data send successfully")
sock.close()
print("Socket closed")
