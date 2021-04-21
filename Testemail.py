import smtplib
from email.message import EmailMessage

class Email(object):
    def __init__(self, to=None, message=None):
        self.to = to
        self.message = message
        self.msg = EmailMessage()

    def verification_email(self, to, uid, code):
        self.to = to
        self.msg['Subject'] = 'Testing Mail Indendations' #"Varification Code From Chess Project SE 2021"
        self.msg['To'] = self.to
        self.msg['From'] = "Chess Project SE 2021"
        self.msg.set_content("Hello,\n\n \tYour varification code for account is 123456")
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login('chessprojectse2021@gmail.com', 'Chess@2021')
                server.send_message(msg)
            return True
        except:
            print("Error while sending the mail to the user {}".format(uid))
            return False


def Send_VerificationCode(to, uid, code):
    msg = EmailMessage()
    msg['Subject'] = 'Verification Code From Chess Project'
    msg['From'] = 'Chess Project SE 2021'
    msg['To'] = to
    msg.set_content('Hello sending test mail for testing function to user {} and code is {}'.format(uid, code))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login('chessprojectse2021@gmail.com', 'Chess@2021')
        server.send_message(msg)
    print("Mail sent")
    return True


Send_VerificationCode(to='malavekarakash2229@yahoo.com', uid="Akash2918", code="123456")

        
        

