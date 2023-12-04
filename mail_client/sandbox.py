import tkinter as tk
from tkinter import Scrollbar

def on_select(event):
    # Lấy các phần tử được chọn từ Listbox
    selected_items = listbox.curselection()
    for i in selected_items:
        print(listbox.get(i))

root = tk.Tk()
root.title("Scrollable Listbox Example")

# Tạo một Listbox
listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)

# Thêm dữ liệu vào Listbox
for i in range(50):
    listbox.insert(tk.END, f"Item {i}")

# Kết hợp Listbox với một Scrollbar
scrollbar = Scrollbar(root, command=listbox.yview)
listbox.config(yscrollcommand=scrollbar.set)

# Gán hàm xử lý sự kiện cho việc chọn phần tử trong Listbox
listbox.bind("<<ListboxSelect>>", on_select)

# Hiển thị Listbox và Scrollbar
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

root.mainloop()
