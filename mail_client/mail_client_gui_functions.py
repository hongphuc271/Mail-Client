from ast import Lambda
import email
from pickle import FALSE
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from webbrowser import get
from mail_client_pop3_func import *
from mail_client_smtp_func import *
from typing import List

#color palates
GOLD = "#fcba03"
GOLD_DARKEN = "#c9960a"
BLUE = "#90e0ef"
WHITE = "#fff"
BLUE_DARKEN = "#029fba"
WHITE_DARKEN = "#c2cdcf"
LIGHTGREY = "#bfc2c9"
TEXT_HIGHLIGHT = "#230f94" 
TEXT_READ = "#8c2ce6"




def app(cfg):
    smtp_addr: tuple
    pop3_addr: tuple
    smtp_addr = (cfg["General"]["mail_server_address"], int(cfg["General"]["smtp_port"]))
    pop3_addr = (cfg["General"]["mail_server_address"], int(cfg["General"]["pop3_port"]))

    user = [cfg["User"]["Username"], cfg["User"]["Password"]]
    pop3_socket = sign_in(pop3_addr, user)
    
    mails : dict = {}
    
    #cửa sổ làm việc chính
    window = tk.Tk()
    window.title("Email Sender")

    window.maxsize(1100,600)

    # thanh làm việc chính, chứa nút viết thư và hộp thư
    sideBar = tk.Frame(window, width=300, height=200, bd= 2)
    sideBar.grid(row=0 ,column= 0, ipadx= 2)
    sideBar.grid_rowconfigure(0, weight=1)
    sideBar.grid_columnconfigure(0, weight=1)
    sideBar.update_idletasks()
    
    
    # khung để làm việc với viết thư và đọc thư, mở ra khi các hàm được chọn, có thể tự đóng lại để tiết kiệm chỗ trống
    emptySpace = tk.Frame(window, padx = 20)
    
    newMailButton = tk.Button(sideBar, text = "+ New Mail", command = lambda: { draft(emptySpace, smtp_addr, user[0]), emptySpace.grid(row = 0, column= 2) }, bd =2, bg=BLUE, padx= 124, pady = 8, cursor="plus")
    newMailButton.grid(row = 0, rowspan = 1, column = 0, columnspan = 3, sticky= "NWE")
    hoverBind(newMailButton, BLUE_DARKEN)
       
    refreshButton = tk.Button(sideBar, text = "refresh", command = lambda: { get_messages(pop3_socket, mails, user), load_all_mails(mails, ".mails/" + user[0]), inbox(mailbox, emptySpace, mails, user[0])}, bd =2, bg=BLUE, padx= 20, pady = 8, cursor= "exchange")
    refreshButton.grid(row= 1, column = 0, columnspan = 1, sticky= "NWE")
    hoverBind(refreshButton, BLUE_DARKEN)
    
    filter_label = tk.Label(sideBar, text = "Filter: ", bg = GOLD)
    filter_label.grid(row = 1, column = 1, sticky = "NSWE")

    filter_list = cfg["Filter"]["List"]
    filterButton = ttk.Combobox(sideBar, values=filter_list)
    filterButton.set("all")
    filterButton.bind("<<ComboboxSelected>>", on_change_filter)
    on_change_filter(selected_value=filterButton.get())   

    filterButton.grid(row = 1, column = 2, columnspan= 1, sticky= "NSWE")
    

    #https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter
    mailbox_canvas = tk.Canvas(sideBar, height= 400, width= 300, borderwidth=0)
    mailbox = tk.Listbox(mailbox_canvas, bg= "#bfc2c9", height= 400, width= 300, selectmode=tk.SINGLE)  
    mailScroll = tk.Scrollbar(sideBar, orient="vertical", command= mailbox_canvas.yview)
    mailbox_canvas.configure(yscrollcommand = mailScroll.set)
    
    mailbox_canvas.grid(row = 3, column= 0, columnspan=3 ,sticky= "NW") 
    mailScroll.grid(row = 3, column = 2, sticky = "NSE")
    mailbox_canvas.create_window((0, 0), window=mailbox, anchor="nw")
    
    mailbox.bind("<Configure>", lambda event, canvas = mailbox_canvas: onFrameConfigure(canvas))
    
    get_messages(pop3_socket, mails, user[0])
    load_all_mails(mails, ".mails/" + user[0])
    inbox(mailbox, emptySpace, mails, user[0])
    
    refresh_time = int(load_config(".mails")["General"]["refresh_time"]) * 1000
    window.after(refresh_time, lambda: on_refresh_timer_timeout(window, refresh_time, mails, emptySpace, mailbox, pop3_socket))
    window.mainloop()

def on_change_filter(event=None, selected_value=None):
    if event:
        selected_value = event.widget.get()

    print("Filter tag changed to " + selected_value)
    save_config(".mails", {"CurrentFilter": {"Tag": selected_value}})
    

# để canvas cuộn được
def onFrameConfigure(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))


def hoverBind(widget, color: str):
    original_color = widget.cget("bg")
    widget.bind("<Enter>", lambda event: on_enter(event, color))# đổi màu widget khi con chuột chỉ vào
    widget.bind("<Leave>", lambda event: on_leave(event, original_color))# đổi màu widget khi con chuột thoát ra
    
def showMTSpace(emptySpace):
    emptySpace.grid(row = 0, column= 2)

def destroy_all_widgets(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    frame.grid_forget()

        
def inbox(window : tk.Frame, mts : tk.Frame, mails : dict, username:str):
    
    #def __init__(self, message_as_string : str, tags : List[str], uidl : str, read : bool):
    #    self.message_as_string : str = message_as_string
    #    self.tags : List[str] = tags
    #    self.uidl : str = uidl
    #    self.read : bool = read
    filter_tag = load_config(".mails")["CurrentFilter"]["Tag"]
    current_scroll_position = window.yview()
    destroy_all_widgets(window)
    window.delete(0, tk.END)
    i = 0
    mail_keys = list(mails.keys())
    for msg_uidl in mail_keys:

        for tag in mails[msg_uidl].tags:
            if filter_tag == tag or filter_tag == "all":
                item = tk.Frame(window, width= 300, height= 50, padx= 2, bg= WHITE, cursor = "hand2", bd =2 )
                item.grid_propagate(False);
                item.update_idletasks()
                Sender = tk.Label(item, text = email.message_from_string(mails[msg_uidl].message_as_string)["From"], bg =WHITE, font=("sans-serif", 8, "bold"))
                Sender.grid(row = 0, column = 0, sticky = "nw")
                if mails[msg_uidl].read == True:
                   Sender.config(foreground = TEXT_READ)
                else:
                   Sender.config(foreground = TEXT_HIGHLIGHT)
            
                tk.Label(item, text = email.message_from_string(mails[msg_uidl].message_as_string)["Subject"], bg =WHITE).grid(row = 1, column = 0, sticky = "nw")
                item.grid(row = i, column = 0, sticky = "N", ipady= 2)
                item.bind("<Button-1>", lambda event ,mts=mts, mail = mails[msg_uidl]: { readMail(event, mts, mail, username), showMTSpace(mts), configRead(mail)})
                hoverBind(item, WHITE_DARKEN)
                window.insert(tk.END, item)
                i = i+1     
                break
                
       
        
    window.yview_moveto(current_scroll_position[0])


def readMail(event ,window, mail: dict, username: str): 
    mail.read = False
    destroy_all_widgets(window)
    message_string = mail.message_as_string
    mail_component = get_message_from_string(message_string)
    
    mailparts = ["Date" ,"From", "To", "Cc", "Bcc", "Subject"]
    i = 0
    for part in mailparts:
         tk.Label(window, text = part + ": ", justify="left").grid(row = i, column = 0, sticky = "NW")
         tk.Label(window, text = mail_component[part], width= 90, anchor = "w").grid(row = i, column = 1, sticky = "NW")
         i = i + 1
    
    body = tk.Text(window, bg = WHITE, width = 80, height=18, padx = 24, relief='flat')
    body.grid(row = 6, column = 0, columnspan=2,sticky= "NW")
    
    attachent_count = 0
    if mail_component.is_multipart():
        for part in mail_component.walk():
            content_type : str = part.get_content_type()
            if content_type == "text/plain":
                body.insert(tk.END, "\n\n" + part.get_payload(decode=True).decode())
            elif content_type.startswith("application"):
                attachent_count += 1
    else:
        body.insert(tk.END, "\n\n" + mail_component.get_payload(decode=True).decode())

    
    body.configure(state='disabled')

    scroll = tk.Scrollbar(window, orient='vertical', command=body.yview)
    scroll.grid(row = 6, column = 1, sticky = "NSE")
    body.configure(yscrollcommand=scroll.set)

    cancel_button = tk.Button(window, text = "Cancel", command=lambda: destroy_all_widgets(window))
    cancel_button.grid(row = 7, column= 0, pady = 10)
    
    file_link = tk.Label(window, text = "there are " + str(attachent_count) + " attachments", cursor= "hand2", padx = 6)
    file_link.grid(row = 7, column = 1)
    file_link.bind("<Button-1>", lambda event: open_file(mail.uidl , username))
    hoverBind(file_link, WHITE_DARKEN)
    

def configRead(mail: dict):
    if mail.read == False:
        mail.read = True
        save_changes_to_mail(mail, ".mails/" + load_config(".mails")["User"]["Username"])


def open_file(m_uidl, username):
    initial_dir = os.path.join(".mails", username, "files", m_uidl)
    
    file_path = filedialog.askopenfilename(
        initialdir=initial_dir,
        title="Select File",
        filetypes=[("All Files", "*.*")]
    )

    if file_path:
        # Use os.startfile to open the file with the default program
        os.startfile(file_path)

def draft(window, smpt_addr, user_name):
    destroy_all_widgets(window)
    client_socket = initiate(smpt_addr)    

    # Tạo các nhãn và ô chỉnh sửa
    tk.Label(window, text="From: ").grid(row=0, column=0, sticky="e")
    tk.Label(window, text = user_name, anchor= "w").grid(row = 0, column = 1, sticky= "we")
    #from_entry = tk.Entry(window)
    #from_entry.grid(row=0, column=1, columnspan=2, sticky="we")

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
    browse_button = tk.Button(window, text="Browse", command=lambda: browse_file(file_paths, window))
    browse_button.grid(row=10, column=0, pady=10)

    # Tạo nút "Send"
    send_button = tk.Button(window, text="Send",
                            command=lambda: send_mail(
                                client_socket,
                                user_name,
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
    
    window.after(5000, lambda:{ keep_connection_alive(client_socket, window)})


def on_enter(event, color:str):
    for widget in event.widget.winfo_children():
        widget.config(bg=color)
    event.widget.config(bg=color)

def on_leave(event, color:str):
    for widget in event.widget.winfo_children():
        widget.config(bg=color)
    event.widget.config(bg=color)  


def browse_file( file_paths : List[str], window):
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
    

def get_messages(client_socket: socket, mails : dict, user_name : str):

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

def on_refresh_timer_timeout(window, refresh_time, mails: dict, empty_space, mailbox, client_socket: socket):
      
    user = load_config(".mails")["User"]["Username"]
    
    get_messages(client_socket, mails, user)
    load_all_mails(mails, ".mails/" + user)
    inbox(mailbox, empty_space, mails, user)
        
    refresh_time = int(load_config(".mails")["General"]["refresh_time"]) * 1000
    print("Refreshed: ", refresh_time)
    window.after(refresh_time, lambda: on_refresh_timer_timeout(window, refresh_time, mails, empty_space, mailbox, client_socket))
        

def keep_connection_alive(client_socket, window, keep_alive_time):
    noop_command = "NOOP\r\n"
    client_socket.send(noop_command.encode())
    client_socket.recv(1024)
    window.after(keep_alive_time * 1000, keep_connection_alive)
    

def login_window(config):
     
    window = tk.Tk()
    window.geometry("400x100")
    tk.Label(text = "Username").grid(row = 0, column= 0)
    tk.Label(text = "Password").grid(row = 1, column= 0)
    username = tk.Entry(window)
    password = tk.Entry(window)
    submit = tk.Button(text = "sign in", command= lambda: { get_user(username.get(), password.get()), window.destroy() })
    submit.grid(row = 2, column= 0, columnspan= 2, sticky = "NW")
    
    username.grid(row=0, column= 1)
    password.grid(row=1, column= 1)
    
    if "User" in load_config(".mails"):
        username = config["User"].get("Username", "Unknown")
        auto_signin = tk.Button(window, text=f"Sign in as {username}", command=lambda: window.destroy())
        auto_signin.grid(row = 0, column = 2)

    window.mainloop()     

def get_user(username:str, password: str):
    save_config(".mails",
                {"User" :
                    {
                        "Username" : username,
                        "Password" : password,
                    }
                }
               )
     