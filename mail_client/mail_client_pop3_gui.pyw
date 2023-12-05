import tkinter as tk
from mail_client_pop3_gui_func import *
from tkinter import ttk
import time

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Mail Client")
root.geometry("600x480")
#root.wm_attributes("-topmost", True)
mail_app = MailApplication(root)
sign_in = UserWindow(root, mail_app)

# Bắt đầu vòng lặp sự kiện
root.mainloop()
