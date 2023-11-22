#from os import *
import os.path
from socket import *
from typing import List
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.utils import formatdate

def initiate(address : tuple) -> socket:
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect(address)
	clientSocket.recv(1024)
	return clientSocket

def draftMail(clientSocket, userMail):
    receipient = input("To: ")
    
    cc = []
    cc.append(input("CC (nhan enter ma khong nhap de thoat): "))
    while cc[-1] != '': #if last != '' : continue, else quit
        cc.append(input())
    cc.pop()

    bcc = []
    bcc.append(input("BCC (nhan enter ma khong nhap de thoat): "))
    while bcc[-1] != '':
        bcc.append(input())
    bcc.pop()
    
    subject = input("Subject: ")
   
    content = input("Content: ")
    
    hasAttachment = input("Attachment? (1 - yes / 0 - no): ")
    
    files = []
    if (hasAttachment == '1'):
       print("filePath (\"/close\" to exit): ")
       while True: 
           path = input()
           
           if (path == "/close"):
               break

           if os.path.isfile(path):
               print("valid file")
               files.append(path)
           else:
               continue
    
    sendMail(clientSocket,	userMail, receipient, cc, bcc, subject, content, attachmentPaths = files)




def sendMail(clientSocket : socket, fromUser : str, toUser : str, ccUsers : List[str], bccUsers : List[str], subject : str, message : str, attachmentPaths : List[str] = []):
	heloCommand : str = 'HELO ' + clientSocket.getsockname()[0] + '\r\n'
	clientSocket.send(heloCommand.encode())
	clientSocket.recv(1024)

	mailFromCommand : str = 'MAIL FROM: %s\r\n' % fromUser
	clientSocket.send(mailFromCommand.encode())
	clientSocket.recv(1024)

	rcptToCommand : str = 'RCPT TO: %s\r\n' % toUser
	clientSocket.send(rcptToCommand.encode())
	clientSocket.recv(1024)
	
	dataCommand = 'DATA\r\n'
	clientSocket.send(dataCommand.encode())
	clientSocket.recv(1024)

	msg = MIMEMultipart()
	msg['From'] = fromUser
	msg['To'] = toUser
	msg['Date'] = formatdate(localtime=True)
	msg['Subject'] = subject

	msg.attach(MIMEText(message))

	for f in attachmentPaths or []:
		with open(f, "rb") as fil:
			part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
		# After the file is closed
		part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
		msg.attach(part)

	clientSocket.send(msg.as_string().encode())
	endMessage = '\r\n.\r\n'
	clientSocket.send(endMessage.encode())
	clientSocket.recv(1024)