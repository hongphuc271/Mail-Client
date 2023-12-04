import tkinter as tk
from mail_client_pop3_gui_func import *
from tkinter import ttk
import subprocess
import time

def on_refresh_timer_timeout():
	get_messages(client_socket, mails, user_info[0])
	tab_bysender.update_message_display()
	tab_all.update_message_display()
	print("Refreshed")
	root.after(refresh_time, on_refresh_timer_timeout) 

#Chạy mail server
run_command = "java -jar test-mail-server-1.0.jar -s 2225 -p 3335 -m .test-mail-server/"
process = subprocess.Popen(run_command, shell=True)
time.sleep(2.0)

# key : str = uidl, value : MailMessage
mails : dict = {}

#Khởi tạo socket và kết nối tới mail server
mail_server = ("127.0.0.1", 3335)
user_info = ("person2@test.net", "person2")
client_socket : socket = sign_in(mail_server, user_info)

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Two-Pane Interface")
root.geometry("600x480")

# Tạo đối tượng Notebook để chứa các tab
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Tạo tab "User"
tab_all = ttk.Frame(notebook)
notebook.add(tab_all, text="User")

load_messages(mails, user_info[0])

#Tạo timer refresh
if not has_config(".mails"):
	save_config(".mails", {"refresh_time" : 5})
refresh_time = int(load_config(".mails")["refresh_time"]) * 1000
root.after(refresh_time, on_refresh_timer_timeout)

tab_bysender = TabBySender(client_socket, notebook, mails, user_info)
tab_all = TabAll(client_socket, notebook, mails, user_info)

# Bắt đầu vòng lặp sự kiện
root.mainloop()
