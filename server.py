import socket
import threading
from database import Database
import pickle

THREADS = []
CLOSE = False
PORT = 12000
IP = ''
DB = Database()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((IP, PORT))
sock.listen(20)

def handle_client(conn, ):
    rec = conn.recv(1024).decode()
    data =  pickle.loads(rec)
    userid, password = data['userid'], data['password']
    if DB.validate_user(username, password):
        data = {
            'ID': 500,
            'Message' : 'Login successfull'
        }
        data = pickle.dumps(data)
        conn.send(data)
        #Starting client
    else:
        data = {
            'ID' : 501,
            'Message' : 'Wrong credentials'
        }
        data = pickle.dumps(data)
        conn.send(data)
        return

def Register_Client(conn, ):
    Exit = False
    while not Exit:
        rev = conn.recv(1024)
        data = pickle.loads(rev)
        id = data['ID']
        if id == 1:
            uid = data['UserID']
            uname = data['Username']
            email = data['Email']
            passwd = data['Password']
            ####Add these fields to Clients table
            try:
                if (DB.Add_new_User(uid, email, Username=uname, Password= passwd)):
                    data = {
                        'ID': 1000,
                        'Message': 'Successful'
                    }
                    continue
                else:
                    data = {
                        'ID' : 1500,
                        'Message': 'User with given email address is already exist'
                    }
            except:
                print("Error while Creating new user with username {}".format(uname))
                data = {
                    'ID' : 2000,
                    'Message' : 'Registration Unsuccessfull'
                }
                # data = pickle.dumps(data)
                # conn.send(data)
                #continue
            ####After success send the message of confermation
            
            data = pickle.dumps(data)
            conn.send(data)
            Exit = True
        else:
            continue



while not CLOSE:
    try:
        conn, addr = sock.accept()
        rec = conn.recv(1024).decode()
        if rec == 'Request':
            conn.send("Connected".encode())
            thread = threading.Thread(target=handle_client, args=(conn,))
            THREADS.append(thread)
            thread.start()
        elif rec == 'Register':
            conn.send("Connected".encode())
            thread1 = threading.Thread(target=Register_Client, args=(conn, ))
            THREADS.append(thread1)
            thread1.start()
        else:
            continue    
    except KeyboardInterrupt:
        CLOSE = True
    except:
        continue



for t in THREADS:
    t.join()