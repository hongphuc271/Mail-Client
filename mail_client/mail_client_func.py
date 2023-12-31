from socket import *
from typing import List
import email
import time
import os
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.utils import formatdate
from os.path import basename

# Class MailMessage lưu nội dung của mail và các thông tin liên qua như
# id của mail; mail đọc hay chưa?; các tag của mail
class MailMessage:
    # Khởi tạo một vài tham số
    def __init__(self, message_as_string : str, tags : List[str], uidl : str, read : bool):
        self.message_as_string : str = message_as_string
        self.tags : List[str] = tags
        self.uidl : str = uidl
        self.read : bool = read

def sign_in(mail_server : tuple, user_info) -> socket:
	client_socket : socket = socket(AF_INET, SOCK_STREAM)
	client_socket.connect(mail_server)
	print("Recv: ", client_socket.recv(1024))


	user_command = "USER %s\r\n" % user_info[0]
	client_socket.send(user_command.encode())
	print("Recv: ", client_socket.recv(1024).decode())

	pass_command = "PASS %s\r\n" % user_info[1]
	client_socket.send(pass_command.encode())
	print("Recv: ", client_socket.recv(1024).decode())

	return client_socket

def end_pop3_session(client_socket : socket):
    quit_command = "QUIT\r\n"
    client_socket.send(quit_command.encode())
    client_socket.recv(1024)
    client_socket.close()

def get_message_count(client_socket : socket) -> int:
    stat_command = "STAT\r\n"
    client_socket.send(stat_command.encode())
    stat = client_socket.recv(1024).decode()
    print("Recv: ", stat)
    #Ex: +OK 12 1024
    message_count = int(stat.split(" ", 2)[1])
    return message_count

def retrieve_message_as_string(client_socket : socket, message_index : int) -> str:
    retr_command = "RETR %d\r\n" % message_index
    client_socket.send(retr_command.encode())
    raw_msg = client_socket.recv(1000000).decode()
    
    checksum_str = raw_msg[4:raw_msg.index("\r\n")]
    checksum = int(checksum_str)
    #Ex: +OK 1024\r\n
    #    ...(message)...
    size_count = len(raw_msg) - 4 - len(checksum_str) - 1
    while size_count < checksum:
        add_data = client_socket.recv(checksum - size_count).decode()
        raw_msg += add_data
        size_count += len(add_data)
        if size_count >= checksum:
            raw_msg += client_socket.recv(8).decode()

    print("Recv: ", raw_msg)
    msg_as_string : str = raw_msg.split("\r\n", 1)[1]
    return msg_as_string

def get_uidl_list(client_socket : socket) -> List[str]:
    uidl_command = "UIDL\r\n"
    client_socket.send(uidl_command.encode())
    uidl = client_socket.recv(1024).decode()
    print("Recv: ", uidl)
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

def get_full_parsed_message(msg_as_string : str) -> str:
    parsed_data = parse_message(msg_as_string)
    msg = parsed_data[0] + parsed_data[1]
    if parsed_data[2] > 1:
        msg += "\nThere are " + str(parsed_data[2]) + " attachments"
    elif parsed_data[2] == 1:
        msg += "\nThere is 1 attachment"
    return msg

# Hàm phân tích dữ liệu từ email chuỗi
# Trả về: (Thông tin cơ bản, Body text, Số file đính kèm) 
def parse_message(msg_as_string : str) -> (str, str, int):
    msg = email.message_from_string(msg_as_string)

    # Lấy thông tin cở bản từ mail
    out_msg = ["", "", 0]
    out_msg[0] += "Date: %s" % msg["Date"]
    out_msg[0] += "\nFrom: %s" % msg["From"]
    out_msg[0] += "\nTo: %s" % msg["To"]
    out_msg[0] += "\nCc: %s" % msg["Cc"]
    out_msg[0] += "\nSubject: %s" % msg["Subject"]

    # Lấy body text và đếm attachment từ mail
    # Refs: https://stackoverflow.com/questions/4094933/python-imap-how-to-parse-multipart-mail-content
    attachent_count = 0
    if msg.is_multipart():
        for part in msg.walk():
            content_type : str = part.get_content_type()
            #print(content_type)
            if content_type == "text/plain":
                out_msg[1] += "\n\n" + part.get_payload(decode=True).decode()
            elif not part.is_multipart():
                attachent_count += 1
    else:
        out_msg[1] += "\n\n" + msg.get_payload(decode=True).decode()
    ####
        
    out_msg[2] = attachent_count

    return tuple(out_msg)

def save_all_mails(mails : dict, folder_path : str):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for m in mails.values():
        save_mail(m, folder_path)

def save_mail(mail : MailMessage, folder_path : str):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    path = folder_path + "/" + mail.uidl
    with open(path, 'w', newline="") as fil:
        fil.write(mail.uidl + "\n")
        fil.write(("1" if mail.read else "0") + "\n")
        fil.write(';'.join(mail.tags) + "\n")
        fil.write(mail.message_as_string)
        print("Saved " + path)
    write_attachments_to_files(mail.message_as_string, folder_path + "/files/" + mail.uidl)

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
            if (not part.is_multipart()) and content_type != "text/plain":
               with open(folder_path + "/" + part.get_filename(), 'wb') as fil:
                   fil.write(part.get_payload(decode=True))

def has_config(folder_path : str):
    return os.path.exists(folder_path + "/config.cfg")

def save_config(folder_path : str, cfg_parameters : dict):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    config = configparser.ConfigParser()

    # Thêm các giá trị vào file cấu hình
    for section in cfg_parameters.keys():
        config[section] = cfg_parameters.get(section, {})

    # Lưu file cấu hình
    with open(folder_path + "/" + 'config.cfg', 'w') as configfile:
        config.write(configfile)

def save_default_config(folder_path : str):
    save_config(".mails",
                {"General" :
                    {
                        "mail_server_address" : "127.0.0.1",
                        "smtp_port" : "2225",
                        "pop3_port" : "3335",
                        "refresh_time" : 10,
                        "username" : "",
                        "password" : "",
                    },
                "Filter" : {
                        "spam" : "subject, content: virus, hack, crack",
                        "project" : "from: person1@test.net, person2@test.net",
                        "important" : "subject, content: urgent, ASAP",
                        "work" : "subject, content: report, meeting",
                    }
                })

def load_config(folder_path : str) -> dict:
    config = configparser.ConfigParser()

    # Đọc file cấu hình
    config.read(folder_path + "/" + "config.cfg")

    # Lấy giá trị từ file cấu hình
    cfg_parameters = {}
    for section in config.sections():
        cfg_parameters[section] = config[section]

    return cfg_parameters

def set_config_param(folder_path : str, section : str, param_name : str, new_value : str):
    config = configparser.ConfigParser()

    # Đọc file cấu hình
    config.read(folder_path + "/" + "config.cfg")

    config.set(section, param_name, new_value)

    # Lưu các thay đổi vào file cấu hình
    with open(folder_path + "/" + 'config.cfg', 'w') as configfile:
        config.write(configfile)

def create_new_message(uidl : str, msg_as_string : str) -> MailMessage:
    new_msg = MailMessage(msg_as_string, [], uidl, False)
    
    #Thêm tag xác định người gửi
    msg = get_message_from_string(msg_as_string)
    sender = msg["From"]
    if sender is None:
        sender = "Unknown"
    new_msg.tags.append("sender:" + sender)
    
    #Thêm tag xác định thư mục
    folders = ["inbox"]
    subject = msg["Subject"]
    content = parse_message(msg_as_string)[1]

    cfg_filters : dict = load_config(".mails").get("Filter", {})

    for filter in cfg_filters:
        #Ex: subject, content: urgent, ASAP
        s = cfg_filters[filter].split(": ", 1)
        target_texts = s[0].split(", ")
        keywords = s[1].split(", ")

        if (not subject is None) and "subject" in target_texts and any(key in subject for key in keywords):
            folders.append(filter)
            if filter == "spam":
                break
            continue
        if (not content is None) and "content" in target_texts and any(key in content for key in keywords):
            folders.append(filter)
            if filter == "spam":
                break
            continue
        if "from" in target_texts and sender in keywords:
            folders.append(filter)
            if filter == "spam":
                break
            continue

    if len(folders) > 0:
        new_msg.tags.append("folder:" + ','.join(folders))

    return new_msg

def initiate_smtp(address : tuple) -> socket:
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(address)
    client_socket.recv(1024)
    
    helo_command : str = 'HELO ' + client_socket.getsockname()[0] + '\r\n'
    client_socket.send(helo_command.encode())
    client_socket.recv(1024)

    return client_socket

def send_mail(client_socket : socket, mailserver : tuple, from_user : str, to_user : str, cc_users : str, bcc_users : str, subject : str, message : str, attachment_paths : List[str] = []):
    if to_user == "" and cc_users == "" and bcc_users == "":
        return
    client_socket = initiate_smtp(mailserver)

    mailfrom_command : str = 'MAIL FROM: %s\r\n' % from_user
    client_socket.send(mailfrom_command.encode())
    client_socket.recv(1024)

    if to_user != "":
        rcptto_command : str = 'RCPT TO: %s\r\n' % to_user
        client_socket.send(rcptto_command.encode())
        client_socket.recv(1024)

    if cc_users != "":
        for ucc in cc_users.split(','):
            cc_rcptto_command : str = 'RCPT TO: %s\r\n' % ucc
            client_socket.send(cc_rcptto_command.encode())
            client_socket.recv(1024)
    if bcc_users != "":
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
    #msg['Bcc'] = bcc_users
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