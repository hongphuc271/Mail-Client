from socket import *
from mail_client_smtp_func import *
from mail_client_pop3_func import *

# Choose a mail server (e.g. Google mail server) and call it mailserver
smtpMailserver : tuple = ("127.0.0.1", 2225)
pop3Mailserver : tuple = ("127.0.0.1", 3335)

# Create socket called clientSocket and establish a TCP connection with mailserver
#AF_INET = IPv4, SOCK_STREAM = TCP

#todo: change socket base on the user's need: send / retrive mail, default is retrival -Phuong
clientSocket : socket = initiate(mailserver)
#usermail : str = 'sender@test.net'

usermail : str = "user@test.net"
login(clientSocket)
draftMail(clientSocket, usermail)



message : str = 'I love computer networking, too!'
sendMail(clientSocket, usermail, 'person1@test.net',
		 '',
		 '',
		 'Hello there!',
		 message,
		 ['C:/Users/Admin/Desktop/cat.jpg']
		 )


