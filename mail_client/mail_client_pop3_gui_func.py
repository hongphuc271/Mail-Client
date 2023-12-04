import tkinter as tk
from mail_client_pop3_func import *
from tkinter import ttk
from typing import Type, List
from socket import *
import os
from tkinter import Scrollbar

def get_messages(client_socket : socket, mails : dict, user_name : str):
    msg_count = get_message_count(client_socket)
    uidl_list = get_uidl_list(client_socket)

    has_new_messages = False

    for i in range(msg_count):
        msg_uidl = uidl_list[i]
        if msg_uidl in mails:
            continue
        has_new_messages = True
        msg_as_string = retrieve_message_as_string(client_socket, i+1)
        
        mails[msg_uidl] = create_new_message(msg_uidl, msg_as_string)
        #mails[msg_uidl] = MailMessage(msg_as_string, ["sender:" + sender], msg_uidl, False)
     
    if has_new_messages:
        save_all_mails(mails, ".mails/" + user_name)

def load_messages(mails : dict, user_name : str):
    load_all_mails(mails, ".mails/" + user_name)

class TabAll:
    def __init__(self, client_socket : socket, notebook : ttk.Notebook, mails : dict, user_info : tuple):
        self.client_socket = client_socket
        self.notebook = notebook
        self.mails = mails
        self.user_info = user_info

        self.run()

    def on_tab_switched_to(self, event):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if current_tab == self.tab_all:
            self.update_message_display()

    def on_message_selected(self, event):
        selected_item = event.widget.curselection()
        if selected_item != ():
            mail : MailMessage = self.mails[self.message_listbox.get(selected_item[0])]

            self.content_label.config(text=get_full_parsed_message(mail.message_as_string))
            if mail.read == False:
                mail.read = True
                self.message_listbox.itemconfig(selected_item, {"bg" : "white"})
                save_changes_to_mail(mail, ".mails/" + self.user_info[0])

    def get_messages_local(self):
        get_messages(self.client_socket, self.mails, self.user_info[0])
        self.update_message_display()
    
    def update_message_display(self):
        self.message_listbox.delete(0, self.message_listbox.size()-1)
        mail_keys = list(self.mails.keys())
        for msg_uidl in mail_keys:
            self.message_listbox.insert(tk.END, msg_uidl)
            if self.mails[msg_uidl].read:
                self.message_listbox.itemconfig(tk.END, {"bg" : "white"})
            else:
                self.message_listbox.itemconfig(tk.END, {"bg" : "lightgray"})

    def run(self):
        # Tạo tab "All"
        self.tab_all = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_all, text="All")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_switched_to, add="+")

        # Tạo Frame chứa danh sách các mục bên trái
        self.left_frame = tk.Frame(self.tab_all)
        self.left_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nw")

        # Tạo danh sách các mục
        self.message_listbox = tk.Listbox(self.left_frame, selectmode=tk.SINGLE, height=0, width=24)
        self.message_listbox.grid(row=0, column=0, sticky="nsew")
        self.message_listbox.bind("<<ListboxSelect>>", self.on_message_selected)

        self.update_message_display()

        # Tạo nút Get messages
        self.get_msg_button = tk.Button(self.tab_all, text="Get messages", command=self.get_messages_local)
        self.get_msg_button.grid(row=0, column = 2)

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

class TabBySender:
    def __init__(self, client_socket : socket, notebook : ttk.Notebook, mails : dict, user_info : tuple):
        self.client_socket = client_socket
        self.notebook = notebook
        self.mails = mails
        self.user_info = user_info
        self.current_section = ""

        self.run()

    def on_tab_switched_to(self, event):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if current_tab == self.tab_bysender:
            self.update_message_display()
    
    def on_sender_selected(self, event):
        selected_item = self.sender_listbox.curselection()
        if selected_item != ():
            self.message_listbox.delete(0, self.message_listbox.size()-1)
            
            current_sender = self.sender_listbox.get(selected_item[0])
            self.choose_sender(current_sender)
            self.current_section = current_sender
    
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

    def on_message_selected(self, event):
        selected_item = self.message_listbox.curselection()
        if selected_item != ():
            mail : MailMessage = self.mails[self.message_listbox.get(selected_item[0])]
            self.content_label.config(text=get_full_parsed_message(mail.message_as_string))
            
            if mail.read == False:
                mail.read = True
                self.message_listbox.itemconfig(selected_item, {"bg" : "white"})
                save_changes_to_mail(mail, ".mails/" + self.user_info[0])

    def get_messages_local(self):
        get_messages(self.client_socket, self.mails, self.user_info[0])
        self.update_message_display()
    
    def update_message_display(self):
        self.sender_listbox.delete(0, self.sender_listbox.size()-1)
        self.message_listbox.delete(0, self.message_listbox.size()-1)
        #content_label.config(text="")

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

    def run(self):
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
        self.get_msg_button.grid(row=0, column = 2)

        # Tạo Frame chứa nội dung bên phải
        self.right_frame = tk.Frame(self.tab_bysender)
        self.right_frame.grid_propagate(False)
        self.right_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        # Tạo Label để hiển thị nội dung của mục được chọn
        self.content_label = tk.Label(self.right_frame, text="Select an item on the left.", anchor="nw", justify="left")
        self.content_label.grid(row=0, column=0)

        self.update_message_display()

        # Thiết lập trọng số của cột và hàng để có thể mở rộng
        self.tab_bysender.columnconfigure(2, weight=1)
        self.tab_bysender.rowconfigure(1, weight=1)

class TabByFolder:
    def __init__(self, client_socket : socket, notebook : ttk.Notebook, mails : dict, user_info : tuple):
        self.client_socket = client_socket
        self.notebook = notebook
        self.mails = mails
        self.user_info = user_info
        self.current_section = ""

        self.run()

    def on_tab_switched_to(self, event):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if current_tab == self.tab_byfolder:
            self.update_message_display()
    
    def on_folder_selected(self, event):
        selected_item = self.folder_listbox.curselection()
        if selected_item != ():
            self.message_listbox.delete(0, self.message_listbox.size()-1)
            
            current_folder = self.folder_listbox.get(selected_item[0])
            self.choose_folder(current_folder)
            self.current_section = current_folder
    
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

    def on_message_selected(self, event):
        selected_item = event.widget.curselection()
        if selected_item != ():
            mail : MailMessage = self.mails[self.message_listbox.get(selected_item[0])]
            self.content_label.config(text=get_full_parsed_message(mail.message_as_string))
            
            if mail.read == False:
                mail.read = True
                self.message_listbox.itemconfig(selected_item, {"bg" : "white"})
                save_changes_to_mail(mail, ".mails/" + self.user_info[0])

    def get_messages_local(self):
        get_messages(self.client_socket, self.mails, self.user_info[0])
        self.update_message_display()
    
    def update_message_display(self):
        self.folder_listbox.delete(0, self.folder_listbox.size()-1)
        self.message_listbox.delete(0, self.message_listbox.size()-1)
        #content_label.config(text="")

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
            self.folder_listbox.insert(tk.END, f)

        self.choose_folder(self.current_section)

    def run(self):
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