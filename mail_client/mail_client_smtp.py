from socket import *
msg = "\r\n I love computer networks!"
endmsg = "\r\n.\r\n"

# Choose a mail server (e.g. Google mail server) and call it mailserver
mailserver = ("127.0.0.1", 2225)

# Create socket called clientSocket and establish a TCP connection with mailserver
#AF_INET = IPv4, SOCK_STREAM = TCP
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(mailserver)

recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '220':
	print('220 reply not received from server.')

# Send HELO command and print server response.
heloCommand = 'HELO Alice\r\n'
clientSocket.send(heloCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)
if recv1[:3] != '250':
	print('250 reply not received from server.')

# Send MAIL FROM command and print server response.
mailFromCommand = 'MAIL FROM: test@client.net\r\n'
clientSocket.send(mailFromCommand.encode())
recv2 = clientSocket.recv(1024).decode()
print(recv2)
if recv2[:3] != '250':
	print('250 reply not received from server.')

# Send RCPT TO command and print server response.
rcptToCommand = 'RCPT TO: person1@test.net\r\n'
clientSocket.send(rcptToCommand.encode())
recv2 = clientSocket.recv(1024).decode()
print(recv2)
if recv2[:3] != '250':
	print('250 reply not received from server.')

# Send DATA command and print server response.
dataCommand = ('DATA\r\n')
clientSocket.send(dataCommand.encode())
recv3 = clientSocket.recv(1024).decode()
print(recv3)
if recv3[:3] != '354':
	print('354 reply not received from server.')

# Send message data.
dataMessage = msg
clientSocket.send(dataMessage.encode())

# Message ends with a single period.
endMessage = endmsg
clientSocket.send(endMessage.encode())
recv4 = clientSocket.recv(1024).decode()
print(recv4)

# Send QUIT command and get server response.
quitCommand = 'QUIT\r\n'
clientSocket.send(quitCommand.encode())
recv5 = clientSocket.recv(1024).decode()
print(recv5)
if recv5[:3] != '221':
	print('221 reply not received from server.')

clientSocket.close()

def draftMail(mailServer):
    print("To: ")
    receipient = input()
    
    print("CC: ")
    cc = ''
    cc = input()
    
    print("BCC: ")
    bcc = ''
    bcc = input()
    
    print("Subject: ")
    subject = input()
    
    print("Content: ")
    content = input()
    
    print("Attachment? (1 - yes / 0 - no): ")
    hasAttachment = input()
    
    files = []
    if (hasAttachment == 1):
       while TRUE:
           print("filePath (\"/close\" to exit): ")
           path = input()
           
           if (path == "/close"):
               break

           if os.path.exists(path):
               files.append(path)
           else:
               continue
    
    sendMail(receipient, cc, bcc, subject, content, files)
  
def sendMail(receipient, cc, bcc, subject, content, files):
    print("do things")  
    #to do: send mail to the server, send file by reading it and send by chunks / any alternitive is fine
    #e.g:
    #   with open(filePath, 'rb') as file:
    #   data = file.read(1024)
    #   while data:
    #      client_socket.send(data)
    #      data = file.read(1024)   
