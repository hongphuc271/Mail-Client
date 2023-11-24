import tkinter as tk
from mail_client_pop3_func import *
from tkinter import ttk

mails = {}

def show_content(selected_item : tuple):
    if selected_item != ():
        content_label.config(text=mails[selected_item[0]][1])

def on_item_selected(event):
    selected_item = listbox.curselection()
    show_content(selected_item)

def get_msg():
    msg_count = get_message_count(client_socket)
    
    mails.clear()
    listbox.delete(0, listbox.size())
    
    for i in range(msg_count):
        msg_as_string = retrieve_message_as_string(client_socket, i+1)
        item_name = "Mail " + str(i+1) #get_message_from_string(msg_as_string)["MessageID"]
        item_content = parse_message(msg_as_string)

        mails[i] = (item_name, item_content)
        listbox.insert(tk.END, item_name)

#Khởi tạo socket và kết nối tới mail server
mail_server = ("127.0.0.1", 3335)
user_info = ("person3@test.net", "person1")
client_socket : socket = sign_in(mail_server, user_info[0], user_info[1])

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Two-Pane Interface")
root.geometry("720x480")

# Tạo đối tượng Notebook để chứa các tab
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Tạo tab "User"
tab_all = ttk.Frame(notebook)
notebook.add(tab_all, text="User")

# Tạo tab "All"
tab_all = ttk.Frame(notebook)
notebook.add(tab_all, text="All")

get_msg_button = tk.Button(tab_all, text="Get messages", command=get_msg)
get_msg_button.grid(row=0, column = 1)

# Tạo Frame chứa danh sách các mục bên trái
left_frame = tk.Frame(tab_all)
left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

# Tạo danh sách các mục
listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE, height=0)
listbox.grid(row=1, column=0, sticky="nsew")
listbox.bind("<<ListboxSelect>>", on_item_selected)

# Tạo Frame chứa nội dung bên phải
right_frame = tk.Frame(tab_all)
right_frame.grid_propagate(False)
right_frame.config(width = 300)
right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

# Tạo Label để hiển thị nội dung của mục được chọn
content_label = tk.Label(right_frame, text="Select an item on the left.", anchor="w", justify="left")
content_label.grid(row=1, column=0)

# Thiết lập trọng số của cột và hàng để có thể mở rộng
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)

# Bắt đầu vòng lặp sự kiện
root.mainloop()
