import socket
import threading
from database import Database
import pickle
from User import Client
import random
import smtplib
from email.message import EmailMessage

THREADS = []
CLOSE = False
PORT = 12000
IP = ''
DB = Database()
Users = []
Rooms = []
QUICK_PLAY = []

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((IP, PORT))
sock.listen(20)

def random_number():
    num = random.randint(100000, 999999)
    return str(num)


def Send_VerificationCode(to, uid, code):
    msg = EmailMessage()
    msg['Subject'] = 'Verification Code From Chess Project'
    msg['From'] = 'Chess Project SE 2021'
    msg['To'] = to
    msg.set_content('Hello {},\n\n \t Your verification code is {}'.format(uid, code))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login('chessprojectse2021@gmail.com', 'Chess@2021')
            server.send_message(msg)
        print("Mail sent1")
        return True
    except:
        return False


def Send_Welcome_Email(to, uid):
    msg = EmailMessage()
    msg['Subject'] = 'Welcome To Chess Project'
    msg['From'] = 'Chess Project SE 2021'
    msg['To'] = to
    msg.set_content('Hello {},\n \t Your account has successfully activated. Lets start the game'.format(uid))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login('chessprojectse2021@gmail.com', 'Chess@2021')
            server.send_message(msg)
        print("Mail sent2")
        return True
    except:
        return False

def handle_client(conn, ):
    Exit = False
    while not Exit:    
        rec = conn.recv(1024).decode()
        data =  pickle.loads(rec)
        id = data['ID']
        userid, password = data['UserID'], data['Password']
        if id == 5:
            if DB.validate_user(username, password):
                data = {
                    'ID': 500,
                    'Message' : 'Login successfull'
                }
                data = pickle.dumps(data)
                conn.send(data)
                #Starting client
                
                c = Client(UserID=userid, conn=conn, database=DB, users=Users, rooms=Rooms)
                Users.append({'UserID':userid, 'conn': conn, 'Client': c})
                c.start()
                Exit = True
            else:
                data = {
                    'ID' : 501,
                    'Message' : 'Invalid credentials'
                }
                data = pickle.dumps(data)
                conn.send(data)
                return
        elif id == 6:           ##Forgot password
            email = data['Email']
            uid = data['UserID']
            
            ncode = random_number()
            Send_VerificationCode(to=email, uid=uid, code=ncode)

        elif id == 2:
            revcode = data['Code']
            if revcode == code:
                newpass = data['Password']
                
                if DB.update_user_password(uid, newpass) :
                    data = {
                        'ID' : 8,
                        'Message': "Password update successful"
                    }
                else:
                    data = {
                        'ID' : 7,
                        'Message' : 'Password update unsuccessful'
                    }
                
            else:
                ncode = random_number()
                Send_VerificationCode(to=email, code=ncode)
                data = {
                    'ID' : 9,
                    'Message':'Invalide Code, new verification code sent'
                }
                
            data = pickle.dumps(data)
            conn.send(data)
        else:
            data = {
                'ID': 7,
                'Message': 'Invalid ID Used for sending message'
            }
            data = pickle.dumps(data)
            conn.send(data)
            
    return

# def forgot_password(conn):
#     EXIT = False
#     while not exit:
#         rev = conn.recv(1024)
#         data = pickle.loads(rev)
#         if id == 1100:
#             email = data['Email']
#             userid = data['UserID']
#             #send these details to database to recover password
#             continue
#         else:
#             data = {
#             'ID': 7,
#             'Message': 'Invalid ID Used for sending message'
#             }
#             data = pickle.dumps(data)
#             conn.send(data)



def Register_Client(conn, ):
    Exit = False
    Variefy = False
    while not Variefy:
        print("Inside the loop register")
        rev = conn.recv(1024)
        data = pickle.loads(rev)
        id = data['ID']
        if id == 1:
            uid = data['UserID']
            # uname = data['Username']
            email = data['Email']
            passwd = data['Password']
            ####Add these fields to Clients table
            #try:
            if (DB.Add_new_User(uid, email, Password= passwd)):
                code = random_number()
                data = {
                    'ID': 1000,
                    'Message': 'Successful but not varified',
                    #'Code' : code,
                }
                #    continue
                # Send email to the client for verification with code
                Send_VerificationCode(email, uid, code)
            else:
                data = {
                    'ID' : 1500,
                    'Message': 'User with given email address is already exist'
                }
            # except:
            #     print("Error while Creating new user with username {}".format(uid))
            #     data = {
            #         'ID' : 2000,
            #         'Message' : 'Registration Unsuccessfull'
            #     }
            #     # data = pickle.dumps(data)
                # conn.send(data)
                #continue
            ####After success send the message of confermation
            
            data = pickle.dumps(data)
            conn.send(data)
            Exit = True
        elif id == 2:
            revcode = data['Code']
            print("Recieved code is {}".format(revcode))
            if revcode == code:
                Variefy = True
                DB.verify_user(uid=uid)
                data = {
                    'ID': 2,
                    'Message': 'Successful and varified',
                }
            else:
                ncode = random_number()
                Send_VerificationCode(to=email, code=ncode)
                data = {
                    'ID' : 9,
                    'Message':'Invalide Code, new verification code sent'
                }
                
            data = pickle.dumps(data)
            conn.send(data)
        else:
            continue
    print("Completed")
    return

print("Server is running on port {}".format(PORT))

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
        # elif rec == 'ForgotPassword':
        #     conn.send("Connected".encode())
        #     thread2 = threading.Thread(target=forgot_password, args=(conn,))
        #     THREADS.append(thread2)
        #     thread2.start()
        else:
            continue    
    except KeyboardInterrupt:
        CLOSE = True
        print('')
        print("Server is closed")
    except:
        continue


# while len(THREADS) > 0:
#     for t in THREADS:
#         t.join()

print("Closing the server..........")