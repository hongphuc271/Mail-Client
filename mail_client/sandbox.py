import tkinter as tk
from tkinter import messagebox

def on_sign_in_clicked():
    # Kiểm tra thông tin đăng nhập
    username = entry_username.get()
    password = entry_password.get()

    # Trong ví dụ này, giả sử username là "admin" và password là "admin123"
    if username == "admin" and password == "admin123":
        # Ẩn Frame đăng nhập
        login_frame.pack_forget()

        # Tạo Frame mới cho cửa sổ chào mừng
        welcome_frame = tk.Frame(root)
        welcome_frame.pack(padx=50, pady=50)

        # Hiển thị dòng chữ Hello World ở giữa Frame mới
        label_hello = tk.Label(welcome_frame, text="Hello World", font=("Helvetica", 20))
        label_hello.pack(pady=20)

    else:
        # Hiển thị thông báo đăng nhập không thành công
        messagebox.showerror("Error", "Invalid username or password")

# Tạo cửa sổ đăng nhập
root = tk.Tk()
root.title("Login")

# Tạo Frame cho cửa sổ đăng nhập
login_frame = tk.Frame(root)
login_frame.pack(padx=50, pady=50)

# Tạo các widget cho Frame đăng nhập
label_username = tk.Label(login_frame, text="Username:")
label_username.pack(pady=10)

entry_username = tk.Entry(login_frame)
entry_username.pack(pady=10)

label_password = tk.Label(login_frame, text="Password:")
label_password.pack(pady=10)

entry_password = tk.Entry(login_frame, show="*")
entry_password.pack(pady=10)

button_sign_in = tk.Button(login_frame, text="Sign In", command=on_sign_in_clicked)
button_sign_in.pack(pady=20)

# Chạy vòng lặp chính của Tkinter
root.mainloop()
