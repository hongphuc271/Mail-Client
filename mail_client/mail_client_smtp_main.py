from socket import *
from mail_client_smtp_func import *
from mail_client_pop3_func import *
from mail_client_gui_functions import *

# Choose a mail server (e.g. Google mail server) and call it mailserver
smtpMailserver : tuple = ("127.0.0.1", 2225)
pop3Mailserver : tuple = ("127.0.0.1", 3335)

# Create socket called clientSocket and establish a TCP connection with mailserver
#AF_INET = IPv4, SOCK_STREAM = TCP

smtpClientSocket : socket = initiate(smtpMailserver)
pop3ClientSocket : socket = initiate(pop3Mailserver)
app(smtpClientSocket, pop3ClientSocket)

