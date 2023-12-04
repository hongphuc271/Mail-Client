from socket import *
from typing import List
import email
import time
import os
import configparser
import poplib


def login(clientSocket: socket, usermail: str, password: str) -> str:
    userCommand: str = "USER %s\r\n" %usermail
    clientSocket.send(userCommand.encode())
    clientSocket.recv(1024)
    
    passCommand = "PASS %s\r\n" %password
    clientSocket.send(passCommand.encode())
    clientSocket.recv(1024)
        
    print("Dang nhap thanh cong")
    return usermail
   

#


def deleteMail(clientSocket: socket, mailId: int):
    deleCommand = "DELE 1\r\n"
    clientSocket.send(deleCommand.encode())

    recv = clientSocket.recv(1024).decode()
    
    
    
class MailMessage:
    # Phương thức khởi tạo
    def __init__(self, message_as_string : str, tags : List[str], uidl : str, read : bool):
        self.message_as_string : str = message_as_string
        self.tags : List[str] = tags
        self.uidl : str = uidl
        self.read : bool = read

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
    message_count = int(stat.split(" ")[1])
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
            fil.write(("1" if m.read else "0") + "\n")
            fil.write(';'.join(m.tags) + "\n")
            fil.write(m.message_as_string)
            print("Saved " + path)
        write_attachments_to_files(m.message_as_string, folder_path + "/files/" + m.uidl)

def save_changes_to_mail(mail : MailMessage, folder_path : str):
    path = folder_path + "/" + mail.uidl
    with open(path, 'w', newline="") as fil:
        fil.write(mail.uidl + "\n")
        fil.write(("1" if mail.read else "0") + "\n")
        fil.write(';'.join(mail.tags) + "\n")
        fil.write(mail.message_as_string)
        print("Saved " + path)
    write_attachments_to_files(mail.message_as_string, folder_path + "/files/" + mail.uidl)

def load_all_mails(mails : dict, folder_path : str):
    if not os.path.exists(folder_path):
        return

    mails.clear()
    for m_path in os.listdir(folder_path):
        path = folder_path + '/' +  m_path
        if os.path.isdir(path):
            continue
        with open(path) as fil:
            m_uidl = fil.readline()[:-1]
            m_read = fil.readline()[:-1] == "1"
            m_tags = fil.readline()[:-1].split(';')
            m_msg = fil.read()
            mails[m_uidl] = MailMessage(m_msg, m_tags, m_uidl, m_read)
            print("Loaded " + path)

def write_attachments_to_files(msg_as_string : str, folder_path : str):
    msg = email.message_from_string(msg_as_string)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if msg.is_multipart():
        for part in msg.walk():
            content_type : str = part.get_content_type()
            if content_type.startswith("application"):
               with open(folder_path + "/" + part.get_filename(), 'wb') as fil:
                   fil.write(part.get_payload(decode=True))

def has_config(folder_path : str):
    return os.path.exists(folder_path + "/config.cfg")

def save_config(folder_path : str, cfg_parameters : dict):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    config = configparser.ConfigParser()

    # Thêm các giá trị vào file cấu hình
    config['Settings'] = cfg_parameters

    # Lưu file cấu hình
    with open(folder_path + "/" + 'config.cfg', 'w') as configfile:
        config.write(configfile)

def load_config(folder_path : str) -> dict:
    config = configparser.ConfigParser()

    # Đọc file cấu hình
    config.read(folder_path + "/" + "config.cfg")

    # Lấy giá trị từ file cấu hình
    return dict(config["Settings"]).copy()