from logging import warning
import mailbox
from pickle import FALSE
from queue import Empty
from sqlite3 import Row
import tkinter as tk
from tkinter import filedialog
from mail_client_smtp_func import *
from typing import List

def app():
    #cửa sổ làm việc chính
    window = tk.Tk()
    window.title("Email Sender")
    #window.minsize(300,400)

    # thanh làm việc chính, chứa nút viết thư và hộp thư
    sideBar = tk.Frame(window, width=300, height=200, bd= 2)
    sideBar.grid(row=0 ,column= 0, ipadx= 2)
    sideBar.grid_rowconfigure(0, weight=1)
    sideBar.grid_columnconfigure(0, weight=1)
    sideBar.update_idletasks()
    
    # khung để làm việc với viết thư và đọc thư, mở ra khi các hàm được chọn, có thể tự đóng lại để tiết kiệm chỗ trống
    emptySpace = tk.Frame(window)
    emptySpace.grid(row = 0, column= 2)
    
    newMailButton = tk.Button(sideBar, text = "+ New Mail", command = lambda: draft(emptySpace), height = 2, bd =2, bg="#90e0ef", padx= 115, cursor="plus")
    newMailButton.grid(row = 0, rowspan = 1, column = 0, columnspan = 1, sticky= "NW")
    
    mailbox = tk.Frame(sideBar, bg= "#bfc2c9", height= 400, width= 300)
    mailbox.grid(row = 1, rowspan= 9, column= 0, sticky= "W")
    #lấy mail từ pop3 và viết nó vào mailbox
    
    window.mainloop()
    
def destroy_all_widgets(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    frame.update_idletasks()
        
def inbox(window):
    #TODO:
    #   1.lấy ra danh sách mail bằng LIST
    #   2.Lấy title, dòng đầu bằng TOP <id> 1
    #   3.In ra từ dữ liệu của 2
    #   4.Lặp lại 2 3 cho đến khi hết danh sách mail
    #   misc: inbox scollable khi overflow
    pass

def readMail(window, mailId: int):
    # TODO:
    #   1.Lấy id từ mail được chọn
    #   2.Lấy mail từ id
    #   3.In ra mail trong emptySpace (window)
    #   4.Có nút để thoát
    pass

def draft(window):
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
    
    #nút này để xóa phần viết thư
    cancel_button = tk.Button(window, text = "Cancel", command=lambda: destroy_all_widgets(window))
    cancel_button.grid(row =12, column= 2, pady = 10)