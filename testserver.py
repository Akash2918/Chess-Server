import socket
import pickle

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("", 12000))
sock.listen(10)

CLOSE = False

while not CLOSE:
    try:
        conn, addr = sock.accept()
        print("Connected to conn = {} and addr = {}".format(conn, addr))
        rev = conn.recv(1024)
        print("The length of data is {}".format(len(rev)))
        data = pickle.loads(rev)
        print(data)
        print("Sent data is User = {} and Password = {}".format(data['Username'], data['Password']))
    except KeyboardInterrupt:
        CLOSE = True
    except:
        print("Erro occured")

