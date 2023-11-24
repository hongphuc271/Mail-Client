from socket import *
from typing import List
import email

def sign_in(mail_server : tuple, user_mail : str, passwords : str) -> socket:
	client_socket : socket = socket(AF_INET, SOCK_STREAM)
	client_socket.connect(mail_server)
	client_socket.recv(1024)

	user_command = "USER %s\r\n" % user_mail
	client_socket.send(user_command.encode())
	client_socket.recv(1024).decode()

	pass_command = "PASS %s\r\n" % passwords
	client_socket.send(pass_command.encode())
	client_socket.recv(1024).decode()

	return client_socket

def get_message_count(client_socket : socket) -> int:
    stat_command = "STAT\r\n"
    client_socket.send(stat_command.encode())
    stat = client_socket.recv(1024).decode()
    #print(stat)
    #Ex: +OK 12 1024
    message_count = int(stat.split(" ", 2)[1])
    #print(message_count)
    return message_count

def retrieve_message_as_string(client_socket : socket, message_index : int) -> str:
    retr_command = "RETR %d\r\n" % message_index
    client_socket.send(retr_command.encode())
    msg_with_headers : str = client_socket.recv(1048576).decode()
    msg_as_string : str = msg_with_headers.split("\n", 1)[1]
    #print('\n\n\n', message_index)
    #Ex: +OK 1024
    #    ...(message)...
    return msg_as_string

def get_message_from_string(msg_as_string : str):
    return email.message_from_string(msg_as_string)

# Hàm phân tích dữ liệu từ email chuỗi
def parse_message(msg_as_string : str) -> str:
    msg = email.message_from_string(msg_as_string)

    # Lưu thông tin từ email
    out_msg = ""
    out_msg += "Date: %s" % msg["Date"]
    out_msg += "\nFrom: %s" % msg["From"]
    out_msg += "\nTo: %s" % msg["To"]
    out_msg += "\nCc: %s" % msg["Cc"]
    #out_msg += "\nBcc: %s" % msg["Bcc"]
    out_msg += "\nSubject: %s" % msg["Subject"]

    # Refs: https://stackoverflow.com/questions/4094933/python-imap-how-to-parse-multipart-mail-content
    attachent_count = 0
    if msg.is_multipart():
        for part in msg.walk():
            content_type : str = part.get_content_type()
            if content_type == "text/plain":
                out_msg += "\n\n" + part.get_payload(decode=True).decode()
            elif content_type.startswith("multipart"):
                attachent_count += 1
    else:
        out_msg += "\n\n" + msg.get_payload(decode=True).decode()
    ####
        
    if attachent_count > 1:
        out_msg += "\n\nThere are %d attachments" % attachent_count
    elif attachent_count == 1:
        out_msg += "\n\nThere is 1 attachment"

    return out_msg
