from socket import *
from mail_client_smtp_func import *

# Choose a mail server (e.g. Google mail server) and call it mailserver
mailserver : tuple = ("127.0.0.1", 2225)

# Create socket called clientSocket and establish a TCP connection with mailserver
#AF_INET = IPv4, SOCK_STREAM = TCP
clientSocket : socket = initiate(mailserver)
usermail : str = 'sender@test.net'

draftMail(clientSocket, usermail)


#message : str = 'I love computer networking, too!'
#sendMail(clientSocket, usermail, ' person1@test.net',
#		 [],
#		 [],
#		 'Hello there!',
#		 message,
#		 ['C:/Users/Admin/Desktop/puppy.jpg']
#		 )

