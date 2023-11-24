
from distutils.command import clean
from socket import *

def login(clientSocket: socket) -> str:
    usermail: str = input("Nhap ten nguoi dung")
    userCommand: str = "USER %s\r\n" %usermail
    clientSocket.send(userCommand.encode())
    clientSocket.recv(1024)
    
    password: str = input("Nhap mat khau nguoi dung")
    passCommand = "PASS %s\r\n" %password
    clientSocket.send(passCommand.encode())
    clientSocket.recv(1024)
        
    print("Dang nhap thanh cong")
    return usermail
   
def printMailList(clientSocket: socket):
    statCommand = "STAT \r\n"
    clientSocket.send(statCommand.encode())
    mailbox = clientSocket.recv(1024).decode()
    
    if mailbox.startswith('+OK'):
        mailCount = int(mailbox.split()[1])
        for i in range(1, mailCount + 1):
            printMail(clientSocket, i)
        
           
def printMail(clientSocket: socket, index: int):
    lineNumber: int = 1
    topCommand: str = "TOP %d %d\r\n" % (index, lineNumber)
    clientSocket.send(topCommand.encode())
        
    mail = clientSocket.recv(1024).decode()
    if mail.startswith("+OK"):
        print(mail[3:])
    

def retrieveMail(clientSocket: socket, mailId: int):
    retrCommand = "RETR %d\r\n" %mailId
    clientSocket.send(retrCommand.encode())

    recv = clientSocket.recv(1024).decode()
    print(recv)
    input("nhan enter de tiep tuc:")
    
def deleteMail(clientSocket: socket, mailId: int):
    deleCommand = "DELE 1\r\n"
    clientSocket.send(deleCommand.encode())

    recv = clientSocket.recv(1024).decode()
    
    
    
    