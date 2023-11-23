import tkinter as tk

def get_text_content():
    # Lấy nội dung từ Text widget
    content = text_widget.get("1.0", "end-1c")
    print("Content:", content)

# Tạo cửa sổ
window = tk.Tk()

# Tạo Text widget
text_widget = tk.Text(window, height=5, width=30)
text_widget.pack()

# Tạo nút để lấy nội dung
get_button = tk.Button(window, text="Get Content", command=get_text_content)
get_button.pack()

# Bắt đầu vòng lặp sự kiện chính
window.mainloop()
