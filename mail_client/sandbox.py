import tkinter as tk

class EmailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email App")

        # Danh sách người gửi email (ListBox bên trái)
        self.sender_listbox = tk.Listbox(root, selectmode=tk.SINGLE)
        self.sender_listbox.grid(row=0, column=0, padx=10, pady=10)
        self.populate_senders()

        # Danh sách email của người được chọn (ListBox ở giữa)
        self.email_listbox = tk.Listbox(root, selectmode=tk.SINGLE)
        self.email_listbox.grid(row=0, column=1, padx=10, pady=10)
        self.sender_listbox.bind("<<ListboxSelect>>", self.populate_emails)

        # Khung hiển thị nội dung email (Frame bên phải)
        self.email_frame = tk.Frame(root, padx=10, pady=10)
        self.email_frame.grid(row=0, column=2, padx=10, pady=10)

    def populate_senders(self):
        # Thêm dữ liệu mẫu vào danh sách người gửi
        senders = ["Alice", "Bob", "Charlie", "David"]
        for sender in senders:
            self.sender_listbox.insert(tk.END, sender)

    def populate_emails(self, event):
        # Xóa nội dung cũ của danh sách email
        self.email_listbox.delete(0, tk.END)

        # Lấy người gửi được chọn
        selected_sender_index = self.sender_listbox.curselection()
        if selected_sender_index:
            sender = self.sender_listbox.get(selected_sender_index)
            
            # Thêm dữ liệu mẫu vào danh sách email của người gửi
            emails = {"Alice": ["Email 1", "Email 2"],
                      "Bob": ["Email 3", "Email 4"],
                      "Charlie": ["Email 5", "Email 6"],
                      "David": ["Email 7", "Email 8"]}
            
            for email in emails.get(sender, []):
                self.email_listbox.insert(tk.END, email)

# Tạo cửa sổ gốc
root = tk.Tk()

# Tạo ứng dụng EmailApp
app = EmailApp(root)

# Chạy vòng lặp chính của ứng dụng
root.mainloop()
