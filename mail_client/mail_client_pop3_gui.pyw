import tkinter as tk
from mail_client_pop3_gui_func import *
from tkinter import ttk
import time

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Mail Client")
root.geometry("720x480")
#Tạo giao diện chính
mail_app = MainWindow(root)
#Tạo giao diện dăng nhập, hiển thị trước khi vào giao diện chính
sign_in = UserWindow(root, mail_app)

# Bắt đầu vòng lặp sự kiện
root.mainloop()
