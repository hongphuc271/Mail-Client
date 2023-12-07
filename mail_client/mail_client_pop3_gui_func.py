import tkinter as tk
from mail_client_pop3_func import *
from tkinter import ttk
from tkinter import filedialog
from typing import Type, List
from socket import *
import os
from tkinter import Scrollbar
import subprocess

#Cửa sổ chính chứa tất cả các tab cần thiết
class MainWindow:
    #Khởi tạo một số tham số
    def __init__(self, root: tk.Tk):
        self.root = root
        self.user_info = ()

    #Hàm gọi khi hết thời gian làm mới mailbox
    def on_refresh_timer_timeout(self):
        get_messages(self)
        
        self.update_all_tabs()
        
        refresh_time = int(load_config(".mails")["General"]["refresh_time"]) * 1000
        refresh_timer = self.root.after(refresh_time, self.on_refresh_timer_timeout)

    def update_all_tabs(self):
        self.tab_bysender.update_message_display()
        self.tab_byfolder.update_message_display()
        self.tab_all.update_message_display()

    #Hàm reset refresh timer
    def reset_refresh_timer(self):
        self.root.after_cancel(self.refresh_timer)

    #Hàm chính để chạy giao diện
    def run(self):
        #Chuẩn bị file config, tạo file config mới nếu chưa có
        if not has_config(".mails"):
            save_default_config(".mails")
        cfg = load_config(".mails")

		#Chạy mail server
        run_command = "java -jar test-mail-server-1.0.jar -s %s -p %s -m .test-mail-server/" % (cfg["General"]["smtp_port"], cfg["General"]["pop3_port"])
        process = subprocess.Popen(run_command, shell=True)
        time.sleep(2.0)
        
        # Biến mails lưu tất cả các mail được load lên từ đĩa
        # Cấu trúc: ( key : str = uidl, value : MailMessage )
        self.mails : dict = {}

		# Khởi tạo socket và kết nối tới mail server
        self.mail_server = (cfg["General"]["mail_server_address"], int(cfg["General"]["pop3_port"]))
        self.client_socket : socket = socket()

        # Tạo đối tượng Notebook để chứa các tab
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        #Load tất cả các mail từ đĩa lên biến mails
        load_messages(self)

        #Tạo timer refresh
        refresh_time = int(load_config(".mails")["General"]["refresh_time"]) * 1000
        self.refresh_timer = self.root.after(refresh_time, self.on_refresh_timer_timeout)

        #Tạo các tab
        self.tab_newmessage = TabNewMessage(self)
        self.tab_all = TabAll(self)
        self.tab_bysender = TabBySender(self)
        self.tab_byfolder = TabByFolder(self)

#Cửa sổ đăng nhập, hiện lên trước khi vào giao diện chính
class UserWindow:
    #Khởi tạo một số biến số và tự động chạy bằng hàm self.run()
    def __init__(self, root : tk.Tk, mail_app : MainWindow):
        self.root = root
        self.mail_app = mail_app
        self.run()

    #Hàm gọi khi nhấp vào nút Đăng nhập
    def on_sign_in_clicked(self):
        # Lưu thông tin đăng nhập
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.mail_app.user_info = (username, password)

        # Ẩn giao diện đăng nhập
        self.login_frame.pack_forget()
        
        #Chạy giao diện chính
        self.mail_app.run()

    #Hàm chính để chạy giao diện
    def run(self):
        # Tạo Frame cho cửa sổ đăng nhập
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(padx=50, pady=50)

        # Tạo các widget cho Frame đăng nhập
        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.pack(pady=10)

        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack(pady=10)

        self.password_label = tk.Label(self.login_frame, text="Password:")
        self.password_label.pack(pady=10)

        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.pack(pady=10)

        self.sign_in_button = tk.Button(self.login_frame, text="Sign In", command=self.on_sign_in_clicked)
        self.sign_in_button.pack(pady=20)

#Hàm lấy mail từ server về máy
def get_messages(mail_app : MainWindow):
    # Khởi tạo connection tới mail_server
    mail_app.client_socket = sign_in(mail_app.mail_server, mail_app.user_info)

    #Lấy số lượng mail trong mailbox và các UIDL tương ứng
    msg_count = get_message_count(mail_app.client_socket)
    uidl_list = get_uidl_list(mail_app.client_socket)

    #Lấy về từ server và tạo object MailMessage cho mỗi mail mới
    has_new_messages = False
    for i in range(msg_count):
        msg_uidl = uidl_list[i]
        if msg_uidl in mail_app.mails:
            continue
        has_new_messages = True
        msg_as_string = retrieve_message_as_string(mail_app.client_socket, i+1)
        
        mail_app.mails[msg_uidl] = create_new_message(msg_uidl, msg_as_string)
    
    #Lưu các mail chưa có trong đĩa về máy
    if has_new_messages:
        save_all_mails(mail_app.mails, ".mails/" + mail_app.user_info[0])

    #Đóng kết nối
    end_pop3_session(mail_app.client_socket)

    #Cập nhật hiển thị cho tất cả các tab
    mail_app.update_all_tabs()

    return has_new_messages

#Hàm load các mail từ đĩa vào biến tạm mails
def load_messages(mail_app : MainWindow):
    load_all_mails(mail_app.mails, ".mails/" + mail_app.user_info[0])

#TabAll hiển thụ tất cả các mail
class TabAll:
    #Khởi tạo một số tham số và tự động chạy bằng hàm self.run()
    def __init__(self, mail_app : MainWindow):
        self.client_socket = mail_app.client_socket
        self.notebook = mail_app.notebook
        self.mails = mail_app.mails
        self.user_info = mail_app.user_info
        self.root = mail_app.root
        self.mail_app = mail_app

        self.run()

    #Hàm dùng để cập nhật mail được hiển thị khi từ tab khác chuyển sang
    def on_tab_switched_to(self, event):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if current_tab == self.tab_all:
            self.update_message_display()

    #Hàm gọi khi một message được chọn, dùng để hiển thị nội dung của mail đó
    def on_message_selected(self, event):
        selected_item = event.widget.curselection()
        if selected_item != ():
            mail : MailMessage = self.mails[self.message_listbox.get(selected_item[0])]

            self.content_label.config(text=get_full_parsed_message(mail.message_as_string))
            if mail.read == False:
                mail.read = True
                self.message_listbox.itemconfig(selected_item, {"bg" : "white"})
                save_changes_to_mail(mail, ".mails/" + self.user_info[0])

    #Hàm gọi khi nhấp vào nút GetMessage
    def get_messages_local(self):
        get_messages(self.mail_app)
        self.update_message_display()
    
    #Hàm để update hiển thị của các mail, trong trường hợp có mail mới
    def update_message_display(self):
        self.message_listbox.delete(0, self.message_listbox.size()-1)
        mail_keys = list(self.mails.keys())
        for msg_uidl in mail_keys:
            self.message_listbox.insert(tk.END, msg_uidl)
            if self.mails[msg_uidl].read:
                self.message_listbox.itemconfig(tk.END, {"bg" : "white"})
            else:
                self.message_listbox.itemconfig(tk.END, {"bg" : "lightgray"})

    #Hàm để chạy giao diện
    def run(self):
        # Tạo tab "All"
        self.tab_all = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_all, text="All")

        # Kết nối event khi một tab được nhấp vào với hàm self.on_tab_switched_to
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_switched_to, add="+")

        # Tạo Frame chứa danh sách các mục bên trái
        self.left_frame = tk.Frame(self.tab_all)
        self.left_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nw")

        # Tạo danh sách các mục
        self.message_listbox = tk.Listbox(self.left_frame, selectmode=tk.SINGLE, height=0, width=24)
        self.message_listbox.grid(row=0, column=0, sticky="nsew")
        self.message_listbox.bind("<<ListboxSelect>>", self.on_message_selected)

        # Cập nhật các hiển thị ngay khi vừa khởi tạo tab này
        self.update_message_display()

        # Tạo nút Get messages
        self.get_msg_button = tk.Button(self.tab_all, text="Get messages", command=self.get_messages_local)
        self.get_msg_button.grid(row=0, column = 1, columnspan = 2) #Chỉnh nút Get Messages về vị trí center(near center)

        # Tạo Frame chứa nội dung bên phải
        self.right_frame = tk.Frame(self.tab_all)
        self.right_frame.grid_propagate(False)
        self.right_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        # Tạo Label để hiển thị nội dung của mục được chọn
        self.content_label = tk.Label(self.right_frame, text="Select an item on the left.", anchor="nw", justify="left")
        self.content_label.grid(row=0, column=0)

        # Thiết lập trọng số của cột và hàng để có thể mở rộng
        self.tab_all.columnconfigure(2, weight=1)
        self.tab_all.rowconfigure(1, weight=1)
       
#TabBySender liệt kê mail theo người gửi
class TabBySender:
    #Khởi tại một vài tham số và tự động chạy bằng hàm self.run()
    def __init__(self, mail_app : MainWindow):
        self.client_socket = mail_app.client_socket
        self.notebook = mail_app.notebook
        self.mails = mail_app.mails
        self.user_info = mail_app.user_info
        self.current_section = ""
        self.root = mail_app.root
        self.mail_app = mail_app

        self.run()

    #Hàm dùng để cập nhật mail được hiển thị khi từ tab khác chuyển sang
    def on_tab_switched_to(self, event):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if current_tab == self.tab_bysender:
            self.update_message_display()
    
    #Hàm gọi khi sender được chọn, dùng để lọc các mail do sender đó gửi
    def on_sender_selected(self, event):
        selected_item = self.sender_listbox.curselection()
        if selected_item != ():
            self.message_listbox.delete(0, self.message_listbox.size()-1)
            
            current_sender = self.sender_listbox.get(selected_item[0])
            self.choose_sender(current_sender)
            self.current_section = current_sender
    
    #Hàm chính để đưa vào message_listbox chỉ các mail mà sender được chọn gửi
    def choose_sender(self, current_sender : str):
        self.current_section = current_sender
        for m in self.mails.values():
            sender = "Unknown"
            for tag in m.tags:
                if tag.startswith("sender:"):
                    sender = tag[7:]
            if sender == current_sender:
                self.message_listbox.insert(tk.END, m.uidl)
                if m.read:
                    self.message_listbox.itemconfig(tk.END, {"bg" : "white"})
                else:
                    self.message_listbox.itemconfig(tk.END, {"bg" : "lightgray"})

    #Hàm gọi khi một message được chọn, dùng để hiển thị nội dung của mail đó
    def on_message_selected(self, event):
        selected_item = self.message_listbox.curselection()
        if selected_item != ():
            mail : MailMessage = self.mails[self.message_listbox.get(selected_item[0])]
            self.content_label.config(text=get_full_parsed_message(mail.message_as_string))
            
            if mail.read == False:
                mail.read = True
                self.message_listbox.itemconfig(selected_item, {"bg" : "white"})
                save_changes_to_mail(mail, ".mails/" + self.user_info[0])
    
    #Hàm gọi khi nhấp vào nút GetMessage
    def get_messages_local(self):
        get_messages(self.mail_app)
        self.update_message_display()
    
    #Hàm để update hiển thị của các mail, trong trường hợp có mail mới
    def update_message_display(self):
        self.sender_listbox.delete(0, self.sender_listbox.size()-1)
        self.message_listbox.delete(0, self.message_listbox.size()-1)

        senders : dict = {}
        for m in self.mails.values():
            sender = "Unknown"
            for tag in m.tags:
                if tag.startswith("sender:"):
                    sender = tag[7:]

            if not (sender in senders):
                senders[sender] = [m]
            else:
                senders[sender].append(m)

        for s in list(senders.keys()):
            self.sender_listbox.insert(tk.END, s)

        self.choose_sender(self.current_section)

    #Hàm chính để chạy giao diện
    def run(self):
        # Kết nối event khi một tab được nhấp vào với hàm self.on_tab_switched_to
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_switched_to, add="+")

        # Tạo tab "BySender"
        self.tab_bysender = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_bysender, text="Senders")

        # Tạo Frame chứa danh sách các mục bên phái
        self.left_frame = tk.Frame(self.tab_bysender)
        self.left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

        # Tạo danh sách các mục
        self.sender_listbox = tk.Listbox(self.left_frame, selectmode=tk.SINGLE, height=0, width=24)
        self.sender_listbox.grid(row=0, column=0, sticky="nsew")
        self.sender_listbox.bind("<<ListboxSelect>>", self.on_sender_selected)

        # Tạo Frame chứa danh sách các mục ở giữa
        self.middle_frame = tk.Frame(self.tab_bysender)
        self.middle_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nw")

        # Tạo danh sách các mục
        self.message_listbox = tk.Listbox(self.middle_frame, selectmode=tk.SINGLE, height=0, width=24)
        self.message_listbox.grid(row=0, column=0, sticky="nsew")
        self.message_listbox.bind("<<ListboxSelect>>", self.on_message_selected)

        # Tạo nút Get messages
        self.get_msg_button = tk.Button(self.tab_bysender, text="Get messages", command=self.get_messages_local)
        self.get_msg_button.grid(row=0, column = 1, columnspan = 2) #Chỉnh nút Get Messages về vị trí center(near center)


        # Tạo Frame chứa nội dung bên phải
        self.right_frame = tk.Frame(self.tab_bysender)
        self.right_frame.grid_propagate(False)
        self.right_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        # Tạo Label để hiển thị nội dung của mục được chọn
        self.content_label = tk.Label(self.right_frame, text="Select an item on the left.", anchor="nw", justify="left")
        self.content_label.grid(row=0, column=0)

        # Cập nhật các hiển thị ngay khi vừa khởi tạo tab này
        self.update_message_display()

        # Thiết lập trọng số của cột và hàng để có thể mở rộng
        self.tab_bysender.columnconfigure(2, weight=1)
        self.tab_bysender.rowconfigure(1, weight=1)

#TabByFolder liệt kê mail theo folder (lọc theo subject, content)
class TabByFolder:
    #Khởi tạo một vài biến số và tự động chạy bằng hàm self.run()
    def __init__(self,  mail_app : MainWindow):
        self.client_socket = mail_app.client_socket
        self.notebook = mail_app.notebook
        self.mails =mail_app. mails
        self.user_info = mail_app.user_info
        self.current_section = ""
        self.root = mail_app.root
        self.mail_app = mail_app

        self.run()

    #Hàm dùng để cập nhật mail được hiển thị khi từ tab khác chuyển sang
    def on_tab_switched_to(self, event):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if current_tab == self.tab_byfolder:
            self.update_message_display()
    
    #Hàm gọi khi folder được chọn, dùng để lọc các mail thuộc vào folder
    def on_folder_selected(self, event):
        selected_item = self.folder_listbox.curselection()
        if selected_item != ():
            self.message_listbox.delete(0, self.message_listbox.size()-1)
            
            current_folder = self.folder_listbox.get(selected_item[0]).lower()
            self.choose_folder(current_folder)
            self.current_section = current_folder
    
    #Hàm chính để đưa vào message_listbox chỉ các mail thuộc folder được chọn
    def choose_folder(self, current_folder : str):
        for m in self.mails.values():
            folders = []
            for tag in m.tags:
                if tag.startswith("folder:"):
                    folders = tag[7:].split(",")
            if current_folder in folders:
                self.message_listbox.insert(tk.END, m.uidl)
                if m.read:
                    self.message_listbox.itemconfig(tk.END, {"bg" : "white"})
                else:
                    self.message_listbox.itemconfig(tk.END, {"bg" : "lightgray"})

     #Hàm gọi khi một message được chọn, dùng để hiển thị nội dung của mail đó
    def on_message_selected(self, event):
        selected_item = event.widget.curselection()
        if selected_item != ():
            mail : MailMessage = self.mails[self.message_listbox.get(selected_item[0])]
            self.content_label.config(text=get_full_parsed_message(mail.message_as_string))
            
            if mail.read == False:
                mail.read = True
                self.message_listbox.itemconfig(selected_item, {"bg" : "white"})
                save_changes_to_mail(mail, ".mails/" + self.user_info[0])

    #Hàm gọi khi nhấp vào nút GetMessage
    def get_messages_local(self):
        get_messages(self.mail_app)
        self.update_message_display()
    
    #Hàm để update hiển thị của các mail, trong trường hợp có mail mới
    def update_message_display(self):
        self.folder_listbox.delete(0, self.folder_listbox.size()-1)
        self.message_listbox.delete(0, self.message_listbox.size()-1)

        display_folders : dict = {}
        for m in self.mails.values():
            folders = []
            for tag in m.tags:
                if tag.startswith("folder:"):
                    folders = tag[7:].split(",")

            for f in folders:
                if f in display_folders:
                    display_folders[f].append(m)
                else:
                    display_folders[f] = [m]

        for f in list(display_folders.keys()):
            self.folder_listbox.insert(tk.END, f.capitalize())

        self.choose_folder(self.current_section)

    #Hàm chính để chạy giao diện
    def run(self):
        # Kết nối event khi một tab được nhấp vào với hàm self.on_tab_switched_to
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_switched_to, add="+")

        # Tạo tab "BySender"
        self.tab_byfolder = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_byfolder, text="Folders")

        # Tạo Frame chứa danh sách các mục bên phái
        self.left_frame = tk.Frame(self.tab_byfolder)
        self.left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

        # Tạo danh sách các mục
        self.folder_listbox = tk.Listbox(self.left_frame, selectmode=tk.SINGLE, height=0, width=24)
        self.folder_listbox.grid(row=0, column=0, sticky="nsew")
        self.folder_listbox.bind("<<ListboxSelect>>", self.on_folder_selected)

        # Tạo Frame chứa danh sách các mục ở giữa
        self.middle_frame = tk.Frame(self.tab_byfolder)
        self.middle_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nw")

        # Tạo danh sách các mục
        self.message_listbox = tk.Listbox(self.middle_frame, selectmode=tk.SINGLE, height=0, width=24)
        self.message_listbox.grid(row=0, column=0, sticky="nsew")
        self.message_listbox.bind("<<ListboxSelect>>", self.on_message_selected)

        # Tạo nút Get messages
        self.get_msg_button = tk.Button(self.tab_byfolder, text="Get messages", command=self.get_messages_local)
        self.get_msg_button.grid(row=0, column = 2)

        # Tạo Frame chứa nội dung bên phải
        self.right_frame = tk.Frame(self.tab_byfolder)
        self.right_frame.grid_propagate(False)
        self.right_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        # Tạo Label để hiển thị nội dung của mục được chọn
        self.content_label = tk.Label(self.right_frame, text="Select an item on the left.", anchor="nw", justify="left")
        self.content_label.grid(row=0, column=0)

        self.update_message_display()

        # Thiết lập trọng số của cột và hàng để có thể mở rộng
        self.tab_byfolder.columnconfigure(2, weight=1)
        self.tab_byfolder.rowconfigure(1, weight=1)

#TabNewMessage dùng để viết thư
class TabNewMessage:
    # Khởi tạo một vài tham số và tự động chạy bằng hàm self.run()
    def __init__(self, mail_app : MainWindow):
        self.notebook = mail_app.notebook
        self.mails = mail_app.mails
        self.user_info = mail_app.user_info
        self.current_section = ""
        self.root = mail_app.root
        self.mail_app = mail_app

        self.run()

    # Hàm gọi khi nhấp vào nút Browse, giúp mở file manager và chọn file, trả về đường dẫn đến file đó trong file_paths
    def browse_file(self, file_paths : List[str]):
        path = filedialog.askopenfilename(initialdir="/", title="Select File", filetypes=(("Text files", "*.txt"), ("All files", "*.*"))) 
        if file_paths.count(path) > 0:
            return
       
        # Giới hạn kích thước tối đa (3 MB)
        file_size = os.stat(path).st_size
        total_size = 0
        for fp in file_paths:
            total_size += os.stat(path).st_size
        if total_size + file_size > 3145728:
            return

        file_paths.append(path)

        # Hiện tên file được chọn
        f_paths_str = ','.join(basename(f) for f in file_paths)
        tk.Label(self.tab_newmessage, text = "%s" % f_paths_str).grid(row = 10, column = 1, sticky="w")

    # Chạy giao diện chính
    def run(self):
        #Load file config
        cfg = load_config(".mails")
    
        # Tạo socket và thiết lập lết nối tới mailsever
        self.mailserver = (cfg["General"]["mail_server_address"], int(cfg["General"]["smtp_port"]))
        self.client_socket : socket = socket()

        # Tạo tab NewMessage
        self.tab_newmessage = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_newmessage, text="New")
    
        # Tạo các nhãn và ô chỉnh sửa
        tk.Label(self.tab_newmessage, text="To:").grid(row=1, column=0, sticky="e")
        to_entry = tk.Entry(self.tab_newmessage)
        to_entry.grid(row=1, column=1, columnspan=2, sticky="we")

        tk.Label(self.tab_newmessage, text="Cc:").grid(row=2, column=0, sticky="e")
        cc_entry = tk.Entry(self.tab_newmessage)
        cc_entry.grid(row=2, column=1, columnspan=2, sticky="we")

        tk.Label(self.tab_newmessage, text="Bcc:").grid(row=3, column=0, sticky="e")
        bcc_entry = tk.Entry(self.tab_newmessage)
        bcc_entry.grid(row=3, column=1, columnspan=2, sticky="we")

        tk.Label(self.tab_newmessage, text="Subject:").grid(row=4, column=0, sticky="e")
        subject_entry = tk.Entry(self.tab_newmessage)
        subject_entry.grid(row=4, column=1, columnspan=2, sticky="we")

        tk.Label(self.tab_newmessage, text="").grid(row=4, column=0, sticky="e")
        message_entry = tk.Text(self.tab_newmessage, height=10, width=40)
        message_entry.grid(row=5, column=1, columnspan=2, sticky="we")

        # Tạo nút "Browse" để chọn file đính kèm
        file_paths = []
        browse_button = tk.Button(self.tab_newmessage, text="Browse", command=lambda: self.browse_file(file_paths))
        browse_button.grid(row=10, column=0, pady=10)

        # Tạo nút "Send"
        send_button = tk.Button(self.tab_newmessage, text="Send",
                                command=lambda: send_mail(
                                    self.client_socket,
                                    self.mailserver,
                                    self.user_info[0],
                                    to_entry.get(),
                                    cc_entry.get(),
                                    bcc_entry.get(),
                                    subject_entry.get(),
                                    message_entry.get("1.0", "end-1c"),
                                    file_paths
                                    )
                                )
        send_button.grid(row=12, column=1, columnspan=2, pady=10)