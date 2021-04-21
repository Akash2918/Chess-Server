# import smtplib
# from email.message import EmailMessage

# msg = EmailMessage()

# msg['Subject'] = 'Testing Mail Indendations'
# msg['From'] = 'Chess Project SE 2021'
# msg['To'] = 'malavekarakash2229@yahoo.com'

# msg.set_content("Test Email from Chess Project SE 2021\n\n \t Testing Indendations")

# server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
# server.login('chessprojectse2021@gmail.com', 'Chess@2021')
# server.send_message(msg)
# server.quit()
# print("Mail sent")

from email import Email

Uemal = Email(to='malavekarakash2229@yahoo.com', message="Hello User")
Uemal.verification_email(to='malavekarakash2229@yahoo.com', uid="Akash2918", code="123456")
print("Done")

