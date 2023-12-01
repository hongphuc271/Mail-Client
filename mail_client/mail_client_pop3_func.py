
from distutils.command import clean
from socket import *

def login(clientSocket: socket, usermail: str, password: str) -> str:
    userCommand: str = "USER %s\r\n" %usermail
    clientSocket.send(userCommand.encode())
    clientSocket.recv(1024)
    
    passCommand = "PASS %s\r\n" %password
    clientSocket.send(passCommand.encode())
    clientSocket.recv(1024)
        
    print("Dang nhap thanh cong")
    return usermail
   
def getMailList(clientSocket: socket):
    statCommand = "STAT\r\n"
    clientSocket.send(statCommand.encode())
    mailbox = clientSocket.recv(1024).decode()
    
    mails = []
    if mailbox.startswith('+OK'):
        mailCount = int(mailbox.split()[1])
        for i in range(1, mailCount + 1):
            mails.append(getMail(clientSocket, i))
            print(getMail(clientSocket, i) + "\n")
    return mails
        
           
def getMail(clientSocket: socket, index: int):
    lineNumber: int = 0
    topCommand: str = "TOP %d %d\r\n" % (index, lineNumber)
    clientSocket.send(topCommand.encode())
        
    mail = clientSocket.recv(1024).decode()
    if mail.startswith("+OK"):
        return(mail[3:])
    

def retrieveMail(clientSocket: socket, mailId: int): 
    retrCommand = "RETR %d\r\n" %mailId
    clientSocket.send(retrCommand.encode())

    response = b""
    while True:
        chunk = clientSocket.recv(1024)
        response += chunk
        if b"\r\n.\r\n" in response:
            break

    print(response.decode())
    return response.decode()
    
def deleteMail(clientSocket: socket, mailId: int):
    deleCommand = "DELE 1\r\n"
    clientSocket.send(deleCommand.encode())

    recv = clientSocket.recv(1024).decode()
    
    
    
    