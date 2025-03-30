import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, simpledialog
from core.file_operations import FileOperations
from core.encryption import FileEncryptor

class NotepadEncryptor:
    def __init__(self, root):
        self.root = root
        self.root.title("Notepad Encryptor")
        self.root.geometry("800x500")
        self.current_file = ""  # file path hiện tại
        self.tabs = []  # Danh sách chứa các Text widget của các tab
        self.file_ops = FileOperations()  # Khởi tạo đối tượng thao tác file
        self.setup_ui()
        
        

      

    def setup_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file_action)
        file_menu.add_command(label="Open", command=self.open_file_action)
        file_menu.add_command(label="Find", command=self.find_file_action)
        file_menu.add_command(label="Save", command=self.save_file_action)
        file_menu.add_command(label="Save As", command=lambda: self.save_file_action(save_as=True))
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo")
        edit_menu.add_command(label="Redo")
        menubar.add_cascade(label="Edit", menu=edit_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Zoom In")
        view_menu.add_command(label="Zoom Out")
        menubar.add_cascade(label="View", menu=view_menu)
        
        menubar.add_command(label="Encrypt", command=self.encrypt_text)
        menubar.add_command(label="Decrypt", command=self.decrypt_text)
        self.root.config(menu=menubar)

        # Tab control
        self.tab_control = ttk.Notebook(self.root)
        self.add_new_tab()  # Thêm tab mặc định
        self.tab_control.pack(expand=1, fill="both")

        # Status Bar
        self.status_bar = tk.Frame(self.root, relief=tk.SUNKEN, height=20, bg="#2C3E50")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.character_label = tk.Label(self.status_bar, text="Character: 0", fg="white", bg="#2C3E50")
        self.character_label.pack(side=tk.LEFT, padx=5)
        self.encrypted_label = tk.Label(self.status_bar, text="Encrypted: No", fg="white", bg="#2C3E50")
        self.encrypted_label.pack(side=tk.LEFT, padx=10)
        self.file_label = tk.Label(self.status_bar, text="File: Untitled", fg="white", bg="#2C3E50")
        self.file_label.pack(side=tk.RIGHT, padx=5)

    def add_new_tab(self, filename="Untitled"):
        # Tạo frame cho tab mới
        new_tab = ttk.Frame(self.tab_control)
        tab_title = f"{filename}  X"
        self.tab_control.add(new_tab, text=tab_title)
        self.tab_control.select(new_tab)  # Chọn tab mới

        # Tạo Text widget cho tab mới
        text_area = tk.Text(new_tab, wrap=tk.WORD, bg="#1C2833", fg="white", insertbackground="white")
        text_area.pack(expand=1, fill="both")
        # Bind sự kiện cập nhật status bar khi người dùng gõ phím
        text_area.bind("<KeyRelease>", lambda event: self.update_status_bar(text_area))
        # Lưu text_area vào danh sách tabs
        self.tabs.append(text_area)

        # Bind sự kiện đóng tab (bắt sự kiện click vào nút X)
        self.tab_control.bind("<Button-1>", self.check_close_tab, add="+")

    def check_close_tab(self, event):
        try:
            clicked_index = self.tab_control.index("@{},{}".format(event.x, event.y))
        except Exception:
            return

        if clicked_index >= 0:
            tab_text = self.tab_control.tab(clicked_index, "text")
            if tab_text.endswith("X"):
                if len(self.tabs) > 1:
                    self.tab_control.forget(clicked_index)
                    del self.tabs[clicked_index]
                else:
                    print("Không thể đóng tab cuối cùng!")

    def get_active_text_area(self):
        # Lấy text widget của tab hiện tại (mặc định lấy phần tử cuối trong danh sách)
        return self.tabs[-1] if self.tabs else None

    def new_file_action(self):
        # Tạo tab mới và reset file hiện tại
        self.add_new_tab("Untitled")
        self.current_file = ""
    
    def open_file_action(self):
        text_area = self.get_active_text_area()
        if text_area:
            file_path = self.file_ops.open_file(text_area, self.root)
            if file_path:
                self.current_file = file_path
                self.root.title(f"Notepad Encryptor - {self.current_file}")
                #Cập nhật tiêu đề tab với tên file mới mở
                current_tab = self.tab_control.select()
                short_name = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
                self.tab_control.tab(current_tab, text=short_name)
                self.update_status_bar(text_area)
    
    def save_file_action(self, save_as=False):
        text_area = self.get_active_text_area()
        if text_area:
            if not self.current_file or save_as:
                file_path = self.file_ops.save_file(text_area, None, save_as)
            else:
                file_path = self.file_ops.save_file(text_area, self.current_file, save_as)
            if file_path:
                self.current_file = file_path
                self.root.title(f"Notepad Encryptor - {self.current_file}")
                current_tab = self.tab_control.index(self.tab_control.select())
                short_name = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\\\')[-1]
                self.tab_control.tab(current_tab, text=short_name)
                self.update_status_bar(text_area)

    def update_status_bar(self, text_area):
        char_count = len(text_area.get("1.0", "end-1c"))
        self.character_label.config(text=f"Character: {char_count}")

    def encrypt_text(self):
    # Yêu cầu nhập key trước khi mã hóa
      key = simpledialog.askstring("Nhập key", "Vui lòng nhập key để mã hóa:", show='*')
    
      if not key:
        messagebox.showerror("Lỗi", "Bạn cần nhập key để tiếp tục mã hóa!")
        return

      self.encryptor = FileEncryptor(key)  # Khởi tạo FileEncryptor với key mới
    
      # Lấy nội dung từ Text widget của tab hiện tại
      text_area = self.get_active_text_area()  # Lấy Text widget đang mở
      if text_area is None:
        messagebox.showerror("Lỗi", "Không tìm thấy vùng nhập văn bản!")
        return
    
      text_content = text_area.get("1.0", tk.END).strip()

      if not text_content:
        messagebox.showerror("Lỗi", "Không có nội dung để mã hóa!")
        return

      # Chọn nơi lưu file mã hóa
      file_path = filedialog.asksaveasfilename(defaultextension=".enc",
                                             filetypes=[("Encrypted Files", "*.enc")])
      if not file_path:
        return
    
      try:
        # Gọi hàm mã hóa trong encryption.py
        encrypted_content = self.encryptor.encrypt_text(text_content)

        # Ghi vào file
        with open(file_path, "wb") as f:
          f.write(encrypted_content)

          messagebox.showinfo("Thành công", "Nội dung đã được mã hóa và lưu!")
      except Exception as e:
          messagebox.showerror("Lỗi", f"Đã có lỗi xảy ra: {e}")


        
        
    def decrypt_text(self):
        messagebox.showinfo("Giải mã", "File đã được giải mã!")
            
            
    def find_file_action(self):
        # Đây là mẫu, bạn có thể tự triển khai chức năng tìm kiếm nội dung trong file
        print("Find file action triggered.")
