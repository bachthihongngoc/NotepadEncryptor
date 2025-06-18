import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

from core.tab_manager import TabManager
from core.decryption import AESDecryptor
from core.file_operations import FileOperations

class NotepadEncryptor:
    def __init__(self, root):
        self.root = root
        self.root.title("Notepad Encryptor")
        self.root.geometry("800x500")

        self.tabs = []
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill="both")
        
        self.tab_manager = TabManager(self.tab_control, self.tabs, self.root)
        self.tab_manager.add_tab()
        
        self.setup_ui()

    def setup_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.tab_manager.add_tab)
        file_menu.add_command(label="Open", command=self.tab_manager.open_file)
        file_menu.add_command(label="Save", command=self.tab_manager.save_file)
        file_menu.add_command(label="Save As", command=lambda: self.tab_manager.
        save_file(save_as=True))
        file_menu.add_command(label="Find", command=self.tab_manager.show_find_bar)
        menubar.add_cascade(label="File", menu=file_menu)
        
        #Encryption Menu
        encrypt_menu = tk.Menu(menubar, tearoff=0)
        encrypt_menu.add_command(label="Encrypt Opened Text", command=self.encrypt_text)
        encrypt_menu.add_command(label="Encrypt File", command=self.encrypt_external_file)
        menubar.add_cascade(label="Encrypt", menu=encrypt_menu)
        
        #Decryption Menu
        decrypt_menu = tk.Menu(menubar, tearoff=0)
        decrypt_menu.add_command(label="Decrypt Opened Text", command=self.decrypt_text)
        #decrypt_menu.add_command(label="Decrypt File", command=self.decrypt_external_file)
        menubar.add_cascade(label="Decrypt", menu=decrypt_menu)

        self.root.config(menu=menubar)

        # Tab widget
        self.tab_control.pack(expand=1, fill="both")

        # Status bar
        self.status_bar = tk.Frame(self.root, relief=tk.SUNKEN, height=20, bg="#2C3E50")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tab_manager.status_bar = self.status_bar

        #ký tự
        self.character_label = tk.Label(self.status_bar, text="", fg="white", bg="#2C3E50")
        self.character_label.pack(side=tk.LEFT, padx=5)
        #truyền label cho TabManager để cập nhật nội dung
        self.tab_manager.character_label = self.character_label

        #dòng
        self.line_label = tk.Label(self.status_bar, text="", fg="white", bg="#2C3E50")
        self.line_label.pack(side=tk.LEFT, padx=5)
        #truyền label cho TabManager để cập nhật dòng
        self.tab_manager.line_label = self.line_label

        #cột
        self.column_label = tk.Label(self.status_bar, text="", fg="white", bg="#2C3E50")
        self.column_label.pack(side=tk.LEFT, padx=5)

        #truyền label cho TabManager để cập nhật cột
        self.tab_manager.column_label = self.column_label



    
        
    def encrypt_text(self):
        self.tab_manager.encrypt_current_tab()

    def encrypt_external_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not filepath:
            return

        key = simpledialog.askstring("Nhập khoá", "Nhập khoá để mã hoá file:", show="*")
        if not key:
            return

        success = FileOperations.encrypt_external_file(filepath, key)
        if success:
            messagebox.showinfo("Thành công", "Đã mã hoá file thành công")
        else:
            messagebox.showerror("Lỗi", "Không thể mã hoá file")
            
    def decrypt_text(self):
      #Giai mã cho IP 2
      current_tab = self.tab_manager.get_current_tab()
      if current_tab:
        encrypted_text = current_tab.get("1.0", "end-1c")
        key = self.prompt_for_key()
        if key:
          try:
            decryptor = AESDecryptor(key)
            decrypted_text = decryptor.decrypt_data(encrypted_text)
            
            #hiện thị nội dung giải mã lên giao diện
            current_tab.delete("1.0", "end")
            current_tab.insert("1.0", decrypted_text)
          
            
            self.tab_manager.update_status_bar(current_tab)

          except Exception as e:
            self.tab_manager.update_status_bar(current_tab)
            print(f"Giải mã thất bại: {e}")
            
    '''def decrypt_external_file(self):
      from core.file_operations import FileOperations
      #giải mã cho IP 1 từ Desktop
      filepath = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
      if filepath:
        key = simpledialog.askstring("Decryption Key", "Nhập khoá giải mã:", show="*")
        if key:
          FileOperations.decrypt_file(filepath, key, self.tab_control, self.tab_manager.text_widgets)'''
          
    def prompt_for_key(self):
      return simpledialog.askstring("Decryption Key", "Nhập khoá để giải mã:", show="*")