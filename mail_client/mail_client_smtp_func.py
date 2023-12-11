
from socket import *
import time
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

def send_mail(smtp_addr: tuple, from_user : str, to_user : str, cc_users : str, bcc_users : str, subject : str, message : str, attachment_paths : List[str] = []):
    #print("To: ", to_user=="")
    client_socket = initiate(smtp_addr)  
    if to_user == "" and cc_users == [] and bcc_users == []:
        return
    helo_command : str = 'HELO ' + client_socket.getsockname()[0] + '\r\n'
    client_socket.send(helo_command.encode())
    client_socket.recv(1024)

    mailfrom_command : str = 'MAIL FROM: %s\r\n' % from_user
    client_socket.send(mailfrom_command.encode())
    client_socket.recv(1024)

    rcptto_command : str = 'RCPT TO: %s\r\n' % to_user
    client_socket.send(rcptto_command.encode())
    client_socket.recv(1024)

    for ucc in cc_users.split(','):
        cc_rcptto_command : str = 'RCPT TO: %s\r\n' % ucc
        client_socket.send(cc_rcptto_command.encode())
        client_socket.recv(1024)

    for ubcc in bcc_users.split(','):
        bcc_rcptto_command : str = 'RCPT TO: %s\r\n' % ubcc
        client_socket.send(bcc_rcptto_command.encode())
        client_socket.recv(1024)

    data_command = 'DATA\r\n'
    client_socket.send(data_command.encode())
    client_socket.recv(1024)

    #Refs: https://stackoverflow.com/questions/3362600/how-to-send-email-attachments
    msg = MIMEMultipart()
    msg['From'] = from_user
    msg['To'] = to_user
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg['Cc'] = cc_users
    msg['Bcc'] = bcc_users
    msg['Message-ID'] = str(time.time()) + "@" + from_user.split("@", 1)[1]

    msg.attach(MIMEText(message))

    for f in attachment_paths or []:
        with open(f, 'rb') as fil:
            fil = open(f, "rb")
            part = MIMEApplication(fil.read(), Name=basename(f))
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)

    client_socket.send(msg.as_string().encode())
    ####

    end_message = '\r\n.\r\n'
    client_socket.send(end_message.encode())
    client_socket.recv(1024)
    end_smtp_session(client_socket)
    

def end_smtp_session(client_socket : socket):
    quit_command = "QUIT\r\n"
    client_socket.send(quit_command.encode())
    client_socket.recv(1024)
    client_socket.close()