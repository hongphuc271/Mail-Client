from socket import *
from typing import List
import email
import time
import os

class MailMessage:
    # Phương thức khởi tạo
    def __init__(self, message_as_string : str, tags : List[str], uidl : str):
        self.message_as_string : str = message_as_string
        self.tags : List[str] = tags
        self.uidl : str = uidl

def sign_in(mail_server : tuple, user_info) -> socket:
	client_socket : socket = socket(AF_INET, SOCK_STREAM)
	client_socket.connect(mail_server)
	client_socket.recv(1024)


	user_command = "USER %s\r\n" % user_info[0]
	client_socket.send(user_command.encode())
	client_socket.recv(1024).decode()

	pass_command = "PASS %s\r\n" % user_info[1]
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
    raw_msg : str = client_socket.recv(104857600).decode()
    msg_as_string : str = raw_msg.split("\r\n", 1)[1]
    #Ex: +OK 1024
    #    ...(message)...
    return msg_as_string

def get_uidl_list(client_socket : socket) -> List[str]:
    uidl_command = "UIDL\r\n"
    client_socket.send(uidl_command.encode())
    uidl = client_socket.recv(1024).decode()
    uidl_list : List[str] = uidl.split('\r\n')
    uidl_list.pop(0)
    for i in range(0, len(uidl_list)):
        if uidl_list[i] == ".":
            uidl_list.pop()
            uidl_list.pop()
            break
        uidl_list[i] = uidl_list[i].split(' ', 1)[1]
    return uidl_list

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

def save_all_mails(mails : dict, folder_path : str):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for m in mails.values():
        path = folder_path + "/" + m.uidl
        with open(path, 'w', newline="") as fil:
            fil.write(m.uidl + "\n")
            fil.write(';'.join(m.tags) + "\n")
            fil.write(m.message_as_string)
            print("Saved " + path)

def load_all_mails(mails : dict, folder_path : str):
    if not os.path.exists(folder_path):
        return

    mails.clear()
    for m_path in os.listdir(folder_path):
        path = folder_path + '/' +  m_path
        with open(path) as fil:
            m_uidl = fil.readline()[:-1]
            m_tags = fil.readline()[:-1].split(';',)
            m_msg = fil.read()
            mails[m_uidl] = MailMessage(m_msg, m_tags, m_uidl)
            print("Loaded " + path)

