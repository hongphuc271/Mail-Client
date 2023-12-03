import tkinter as tk
from mail_client_pop3_func import *
from tkinter import ttk
from typing import Type, List
from socket import *
import os

def get_messages(client_socket : socket, mails : dict, user_name : str):
    msg_count = get_message_count(client_socket)
    uidl_list = get_uidl_list(client_socket)

    for i in range(msg_count):
        msg_uidl = uidl_list[i]
        if msg_uidl in mails:
            continue
        msg_as_string = retrieve_message_as_string(client_socket, i+1)
        sender = email.message_from_string(msg_as_string)["From"]
        if sender is None:
            sender = "Unknown"
        mails[msg_uidl] = MailMessage(msg_as_string, ["sender:" + sender], msg_uidl)
        
    save_all_mails(mails, ".mails/" + user_name)

def load_messages(mails : dict, user_name : str):
    load_all_mails(mails, ".mails/" + user_name)

def launch_tab_all(client_socket : socket, notebook : ttk.Notebook, mails : dict, user_info : tuple):
    def on_message_selected(event):
        selected_item = event.widget.curselection()
        if selected_item != ():
            content_label.config(text=parse_message(mails[message_listbox.get(selected_item[0])].message_as_string))
    
    def get_messages_local():
        get_messages(client_socket, mails, user_info[0])
        update_message_display()
    
    def update_message_display():
        message_listbox.delete(0, message_listbox.size()-1)
        mail_keys = list(mails.keys())
        for msg_uidl in mail_keys:
            message_listbox.insert(tk.END, msg_uidl)

    # Tạo tab "All"
    tab_all = ttk.Frame(notebook)
    notebook.add(tab_all, text="All")

    # Tạo Frame chứa danh sách các mục bên trái
    left_frame = tk.Frame(tab_all)
    left_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nw")

    # Tạo danh sách các mục
    message_listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE, height=0, width=24)
    message_listbox.grid(row=0, column=0, sticky="nsew")
    message_listbox.bind("<<ListboxSelect>>", on_message_selected)

    update_message_display()

    # Tạo nút Get messages
    get_msg_button = tk.Button(tab_all, text="Get messages", command=get_messages_local)
    get_msg_button.grid(row=0, column = 2)

    # Tạo Frame chứa nội dung bên phải
    right_frame = tk.Frame(tab_all)
    right_frame.grid_propagate(False)
    right_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

    # Tạo Label để hiển thị nội dung của mục được chọn
    content_label = tk.Label(right_frame, text="Select an item on the left.", anchor="nw", justify="left")
    content_label.grid(row=0, column=0)

    # Thiết lập trọng số của cột và hàng để có thể mở rộng
    tab_all.columnconfigure(2, weight=1)
    tab_all.rowconfigure(1, weight=1)

def launch_tab_bysender(client_socket : socket, notebook : ttk.Notebook, mails : dict, user_info : tuple):
    def on_sender_selected(event):
        selected_item = event.widget.curselection()
        if selected_item != ():
            message_listbox.delete(0, message_listbox.size()-1)
            
            current_sender = sender_listbox.get(selected_item[0])
            for m in mails.values():
                sender = "Unknown"
                for tag in m.tags:
                    if tag.startswith("sender:"):
                        sender = tag[7:]
                if sender == current_sender:
                    message_listbox.insert(tk.END, m.uidl)
    
    def on_message_selected(event):
        selected_item = event.widget.curselection()
        if selected_item != ():
            content_label.config(text=parse_message(mails[message_listbox.get(selected_item[0])].message_as_string))

    def get_messages_local():
        get_messages(client_socket, mails, user_info[0])
        update_message_display()
    
    def update_message_display():
        sender_listbox.delete(0, sender_listbox.size()-1)
        message_listbox.delete(0, message_listbox.size()-1)
        #content_label.config(text="")

        senders : dict = {}
        for m in mails.values():
            sender = "Unknown"
            for tag in m.tags:
                if tag.startswith("sender:"):
                    sender = tag[7:]

            if not (sender in senders):
                senders[sender] = [m]
            else:
                senders[sender].append(m)

        for s in list(senders.keys()):
            sender_listbox.insert(tk.END, s)
            

    # Tạo tab "BySender"
    tab_bysender = ttk.Frame(notebook)
    notebook.add(tab_bysender, text="Senders")

    # Tạo Frame chứa danh sách các mục bên phái
    left_frame = tk.Frame(tab_bysender)
    left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

    # Tạo danh sách các mục
    sender_listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE, height=0, width=24)
    sender_listbox.grid(row=0, column=0, sticky="nsew")
    sender_listbox.bind("<<ListboxSelect>>", on_sender_selected)

    # Tạo Frame chứa danh sách các mục ở giữa
    middle_frame = tk.Frame(tab_bysender)
    middle_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nw")

    # Tạo danh sách các mục
    message_listbox = tk.Listbox(middle_frame, selectmode=tk.SINGLE, height=0, width=24)
    message_listbox.grid(row=0, column=0, sticky="nsew")
    message_listbox.bind("<<ListboxSelect>>", on_message_selected)

    # Tạo nút Get messages
    get_msg_button = tk.Button(tab_bysender, text="Get messages", command=get_messages_local)
    get_msg_button.grid(row=0, column = 2)

    # Tạo Frame chứa nội dung bên phải
    right_frame = tk.Frame(tab_bysender)
    right_frame.grid_propagate(False)
    right_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

    # Tạo Label để hiển thị nội dung của mục được chọn
    content_label = tk.Label(right_frame, text="Select an item on the left.", anchor="nw", justify="left")
    content_label.grid(row=0, column=0)

    update_message_display()

    # Thiết lập trọng số của cột và hàng để có thể mở rộng
    tab_bysender.columnconfigure(2, weight=1)
    tab_bysender.rowconfigure(1, weight=1)