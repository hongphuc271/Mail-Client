import tkinter as tk

def get_selected_index():
    selected_index = listbox.curselection()
    if selected_index:
        print("Chỉ mục của phần tử được chọn:", selected_index[0])
    else:
        print("Không có phần tử nào được chọn.")

# Tạo cửa sổ
window = tk.Tk()
window.title("Lấy chỉ mục của phần tử trong Listbox")

# Tạo Listbox
listbox = tk.Listbox(window)
listbox.pack(pady=10)

# Thêm một số mục vào Listbox
items = ["Item 1", "Item 2", "Item 3"]
for item in items:
    listbox.insert(tk.END, item)

# Tạo nút để lấy chỉ mục của phần tử được chọn
button = tk.Button(window, text="Lấy chỉ mục", command=get_selected_index)
button.pack(pady=10)

# Chạy ứng dụng
window.mainloop()
