import tkinter as tk
from tkinter import filedialog
from mail_client_smtp_func import *
from typing import List
import os
import subprocess
import time

def keep_connection_alive():
    noop_command = "NOOP\r\n"
    client_socket.send(noop_command.encode())
    client_socket.recv(1024)
    window.after(5000, keep_connection_alive)

def browse_file(file_paths : List[str]):
    path = filedialog.askopenfilename(initialdir="/", title="Select File", filetypes=(("Text files", "*.txt"), ("All files", "*.*"))) 
    if file_paths.count(path) > 0:
        return
    
    file_paths.append(path)
    file_size = os.stat(path).st_size
    total_size = 0
    for fp in file_paths:
        total_size += os.stat(path).st_size
    
    if total_size + file_size > 3145728:
        return

    # Hiện tên file được chọn
    f_paths_str = ','.join(basename(f) for f in file_paths)
    tk.Label(window, text = " Selected files: %s" % f_paths_str).grid(row = 10, column = 1, sticky="w")

#Chạy mail server
run_command = "java -jar test-mail-server-1.0.jar -s 2225 -p 3335 -m .test-mail-server/"
process = subprocess.Popen(run_command, shell=True)
time.sleep(2.0)

# Tạo socket và thiết lập lết nối tới mailsever
mailserver = ("127.0.0.1", 2225)
client_socket = initiate(mailserver)

helo_command : str = 'HELO ' + client_socket.getsockname()[0] + '\r\n'
client_socket.send(helo_command.encode())
client_socket.recv(1024)

# Tạo cửa sổ
window = tk.Tk()
window.title("Email Sender")

# Tạo các nhãn và ô chỉnh sửa
tk.Label(window, text="From:").grid(row=0, column=0, sticky="e")
from_entry = tk.Entry(window)
from_entry.grid(row=0, column=1, columnspan=2, sticky="we")

tk.Label(window, text="To:").grid(row=1, column=0, sticky="e")
to_entry = tk.Entry(window)
to_entry.grid(row=1, column=1, columnspan=2, sticky="we")

tk.Label(window, text="Cc:").grid(row=2, column=0, sticky="e")
cc_entry = tk.Entry(window)
cc_entry.grid(row=2, column=1, columnspan=2, sticky="we")

tk.Label(window, text="Bcc:").grid(row=3, column=0, sticky="e")
bcc_entry = tk.Entry(window)
bcc_entry.grid(row=3, column=1, columnspan=2, sticky="we")

tk.Label(window, text="Subject:").grid(row=4, column=0, sticky="e")
subject_entry = tk.Entry(window)
subject_entry.grid(row=4, column=1, columnspan=2, sticky="we")

tk.Label(window, text="").grid(row=4, column=0, sticky="e")
message_entry = tk.Text(window, height=10, width=40)
message_entry.grid(row=5, column=1, columnspan=2, sticky="we")

# Tạo nút "Browse" để chọn file đính kèm
file_paths = []
browse_button = tk.Button(window, text="Browse", command=lambda: browse_file(file_paths))
browse_button.grid(row=10, column=0, pady=10)

# Tạo nút "Send"
send_button = tk.Button(window, text="Send",
                        command=lambda: send_mail(
                            client_socket,
                            from_entry.get(),
                            to_entry.get(),
                            cc_entry.get(),
                            bcc_entry.get(),
                            subject_entry.get(),
                            message_entry.get("1.0", "end-1c"),
                            file_paths
                            )
                        )
send_button.grid(row=12, column=1, columnspan=2, pady=10)

window.after(5000, keep_connection_alive)

# Main loop
window.mainloop()
