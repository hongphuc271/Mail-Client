import tkinter as tk

def update_label():
    # Hàm bạn muốn thực hiện sau mỗi khoảng thời gian
    label.config(text="Updated at least every 1000 milliseconds")
    # Gọi lại hàm sau 1000 milliseconds (1 giây)
    root.after(1000, update_label)

# Tạo cửa sổ tkinter
root = tk.Tk()
root.title("Timer Example")

# Tạo một label để hiển thị thông tin
label = tk.Label(root, text="Initial Text")
label.pack(padx=10, pady=10)

# Bắt đầu timer bằng cách gọi hàm đầu tiên
update_label()

# Main loop của tkinter
root.mainloop()
