from socket import *
msg = "\r\n I love computer networks!"
endmsg = "\r\n.\r\n"

# Choose a mail server (e.g. Google mail server) and call it mailserver
mailserver = ("127.0.0.1", 3335)

# Create socket called clientSocket and establish a TCP connection with mailserver
#AF_INET = IPv4, SOCK_STREAM = TCP
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(mailserver)

recv = clientSocket.recv(1024).decode()
print(recv)

#Create account
userCommand = "USER test@client.net\r\n"
clientSocket.send(userCommand.encode())

recv1 = clientSocket.recv(1024).decode()
print(recv1)

passCommand = "PASS testpass\r\n"
clientSocket.send(passCommand.encode())

recv2 = clientSocket.recv(1024).decode()
print(recv2)

#Check mailbox's status
statCommand = "STAT\r\n"
clientSocket.send(statCommand.encode())

recv3 = clientSocket.recv(1024).decode()
print(recv3)

listCommand = "LIST\r\n"
clientSocket.send(listCommand.encode())

recv4 = clientSocket.recv(1024).decode()
print(recv4)

#Retrieve a message  
retrCommand = "RETR 1\r\n"
clientSocket.send(retrCommand.encode())

recv5 = clientSocket.recv(1024).decode()
print(recv5)

#Delete a message
deleCommand = "DELE 1\r\n"
clientSocket.send(deleCommand.encode())

recv6 = clientSocket.recv(1024).decode()
print(recv6)

#Reset session
rsetCommand = "RSET\r\n"
clientSocket.send(rsetCommand.encode())

recv7 = clientSocket.recv(1024).decode()
print(recv7)

#Return part of messages
topCommand = "TOP 1 10\r\n"
clientSocket.send(topCommand.encode())

recv8 = clientSocket.recv(1024).decode()
print(recv8)

#Quit
quitCommand = "QUIT\r\n"
clientSocket.send(quitCommand.encode())

recv9 = clientSocket.recv(1024).decode()
print(recv9)

clientSocket.close()