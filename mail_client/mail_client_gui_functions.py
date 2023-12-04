from ast import Lambda
from cProfile import label
import email
from email.iterators import body_line_iterator
from logging import warning
import mailbox
from pickle import FALSE
from queue import Empty
from smtplib import SMTP
from sqlite3 import Row
from textwrap import wrap
import tkinter as tk
from tkinter import filedialog
from turtle import color
from mail_client_pop3_func import *
from mail_client_smtp_func import *
from typing import List

#color palates
BLUE = "#90e0ef"
WHITE = "#fff"
BLUE_DARKEN = "#029fba"
WHITE_DARKEN = "#c2cdcf"
LIGHTGREY = "#bfc2c9"
TEXT_HIGHLIGHT = "#230f94" 

def app(smtpSocket, pop3Socket):
    
    get_mail_state = [" log in ", "get mail"]
    #cửa sổ làm việc chính
    window = tk.Tk()
    window.title("Email Sender")

    window.maxsize(1000,500)

    # thanh làm việc chính, chứa nút viết thư và hộp thư
    sideBar = tk.Frame(window, width=300, height=200, bd= 2)
    sideBar.grid(row=0 ,column= 0, ipadx= 2)
    sideBar.grid_rowconfigure(0, weight=1)
    sideBar.grid_columnconfigure(0, weight=1)
    sideBar.update_idletasks()
    
    
    # khung để làm việc với viết thư và đọc thư, mở ra khi các hàm được chọn, có thể tự đóng lại để tiết kiệm chỗ trống
    emptySpace = tk.Frame(window)
  
    
    newMailButton = tk.Button(sideBar, text = "+ New Mail", command = lambda: { draft(emptySpace, smtpSocket), emptySpace.grid(row = 0, column= 2) }, height = 2, bd =2, bg=BLUE, padx= 115, cursor="plus")
    newMailButton.grid(row = 0, rowspan = 1, column = 0, columnspan = 1, sticky= "NW")
    hoverBind(newMailButton, BLUE_DARKEN)
    
    refreshButton = tk.Button(sideBar, text = get_mail_state[user != "unknown"], command = lambda: {login(pop3Socket, "inbox@testmail.net", "testpass") if user == "unknown" else inbox(mailbox, pop3Socket, emptySpace)}, height = 2, bd =2, bg=BLUE, padx= 124, cursor= "exchange")
    refreshButton.grid(row= 1, column = 0, columnspan = 1, sticky= "NW")
    hoverBind(refreshButton, BLUE_DARKEN)
    
    
    #https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter
    mailbox_canvas = tk.Canvas(sideBar, height= 400, width= 294, borderwidth=0)
    mailbox = tk.Frame(mailbox_canvas, bg= "#bfc2c9", height= 400, width= 300)  
    mailScroll = tk.Scrollbar(sideBar, orient="vertical", command= mailbox_canvas.yview)
    
    mailbox_canvas.configure(yscrollcommand = mailScroll.set)
    
    mailbox_canvas.grid(row = 2, column= 0, sticky= "NW") 
    mailScroll.grid(row = 2, column = 0, sticky = "NSE")
    mailbox_canvas.create_window((0, 0), window=mailbox, anchor="nw")
    
    mailbox.bind("<Configure>", lambda event, canvas=mailbox_canvas: onFrameConfigure(canvas))

    sideBar.grid(row=0 ,column= 0, ipadx= 2)
    sideBar.update_idletasks()
    window.mainloop()

def onFrameConfigure(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))

def hoverBind(widget, color: str):
    original_color = widget.cget("bg")
    widget.bind("<Enter>", lambda event: on_enter(event, color))
    widget.bind("<Leave>", lambda event: on_leave(event, original_color))

def showMTSpace(emptySpace):
    emptySpace.grid(row = 0, column= 2)

def destroy_all_widgets(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    frame.grid_forget()

        
def inbox(window, pop3Socket, mts):
    #TODO:
    #   1.lấy ra danh sách mail bằng LIST
    #   2.Lấy title, dòng đầu bằng TOP <id> 1
    #   3.In ra từ dữ liệu của 2
    #   4.Lặp lại 2 3 cho đến dkhi hết danh sách mail
    
    mails = getMailList(pop3Socket)
    mailItems = []
    print(mailItems)
    i=1
    for mail in mails:
        text = mail.split('\n')
        FROM: str
        SUBJECT: str
        for chunk in text:
            if chunk.startswith('From:'):
                FROM = chunk[5:]
            elif chunk.startswith("Subject:"):
                SUBJECT = chunk[8:]

        item = tk.Frame(window, width= 296, height= 50, padx= 2, bg= WHITE, cursor = "hand2", bd =2 )
        item.grid_propagate(False);
        item.update_idletasks()
        tk.Label(item, text = FROM, foreground = TEXT_HIGHLIGHT, bg =WHITE, font=("sans-serif", 8, "bold")).grid(row = 0, column = 0, sticky = "nw")
        tk.Label(item, text = SUBJECT, bg =WHITE).grid(row = 1, column = 0, sticky = "nw")
        
        item.grid(row = i-1, column = 0, sticky = "N", ipady= 2)
        item.bind("<Button-1>", lambda event ,mts=mts, index=i, pop3Socket=pop3Socket: { readMail(event, mts, index, pop3Socket), showMTSpace(mts) })
        hoverBind(item, WHITE_DARKEN)
        i = i + 1
        
       
        mailItems.append(item)
        

    #   misc: inbox scollable khi overflow

def readMail(event ,window, mailId: int, pop3Socket): 
    # TODO:
    #   1.Lấy id từ mail được chọn
    #   2.Lấy mail từ id
    #   3.In ra mail trong emptySpace (window)
    #   4.Có nút để thoát
    destroy_all_widgets(window)
    mail = email.message_from_string(retrieveMail(pop3Socket, mailId))
    
    mailparts = ["Date" ,"From", "To", "Cc", "Bcc", "Subject"]
    i = 0
    for part in mailparts:
         tk.Label(window, text = part + ": ", justify="left").grid(row = i, column = 0, sticky = "NW")
         tk.Label(window, text = mail.get_all(part, []), width= 90, anchor = "w").grid(row = i, column = 1, sticky = "NW")
         i = i + 1
    
    body = tk.Text(window, bg = WHITE, width = 80, height=18, padx = 24, relief='flat')
    body.grid(row = 6, column = 0, columnspan=2,sticky= "NW")
    body.insert(tk.END, "\n".join(body_line_iterator(mail)))
    body.configure(state='disabled')

    scroll = tk.Scrollbar(window, orient='vertical', command=body.yview)
    scroll.grid(row = 6, column = 1, sticky = "NSE")
    body.configure(yscrollcommand=scroll.set)

    cancel_button = tk.Button(window, text = "Cancel", command=lambda: destroy_all_widgets(window))
    cancel_button.grid(row = 7, column= 0, pady = 10)

def draft(window, client_socket):
    destroy_all_widgets(window)
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
                            command=lambda: sendMail(
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




def on_enter(event, color:str):
    for widget in event.widget.winfo_children():
        widget.config(bg=color)
    event.widget.config(bg=color)

def on_leave(event, color:str):
    for widget in event.widget.winfo_children():
        widget.config(bg=color)
    event.widget.config(bg=color)  
    