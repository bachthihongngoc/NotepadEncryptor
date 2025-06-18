from pathlib import Path, os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from core.encryption import AESEncryptor
from core.decryption import AESDecryptor
from ui.dialogs import Dialogs
import base64



class FileOperations:
    @staticmethod
    def new_file(text_area, root):
        text_area.delete("1.0", tk.END)
        root.title("Notepad Encryptor - New File")
        return ""  # reset file path
    
    @staticmethod
    def read_file():
      file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
      if not file_path:
        return None, None, False

      try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
          content = file.read()

          #kiểm tra content đã đọc
          #print("content đã đọc:", content)

        is_encrypted_file = FileOperations.is_encrypted(file_path)
        '''ext = os.path.splitext(file_path)[1].lower()
        is_encrypted = (ext == ".enc")'''

        if  is_encrypted_file:
          key = Dialogs.ask_decryption_key()
          if key:
            try:
              #encrypted_data = base64.b64decode(content)
              #print("content:", content)
              decryptor = AESDecryptor(key)
              decrypt_content = decryptor.decrypt_data(content)
            except Exception as e:
              if "decode" in str(e) or "wrong key" in str(e).lower():
                Dialogs.show_wrong_decryption_key()
              else:
                return None, None, False
          else:
          # Không nhập key, giữ nguyên nội dung mã hoá
            decrypt_content = content
        else:
           decrypt_content = content

        return file_path, decrypt_content, is_encrypted_file

      except Exception as e:
        Dialogs.show_open_file_error(e)
        return None, None, False

    
    
    @staticmethod
    def save_file(text_area, current_file, save_as=False):
      global current_file_path  # Biến toàn cục để lưu file_path
      current_file_path = None

      if save_as or not current_file:  # Khi Save As hoặc file chưa có
        # Lần đầu lưu, yêu cầu nhập key mã hóa trước
        key = Dialogs.prompt_for_key_encrypt()
        plaintext = text_area.get("1.0", "end-1c")  # Lấy toàn bộ nội dung trong text_area

        if key:
          try:
              # Mã hóa toàn bộ nội dung trong text_area, chuyển chuỗi thành bytes
              encryptor = AESEncryptor(key)
              encrypted_content = encryptor.encrypt(plaintext.encode("utf-8"))  # Chuyển văn bản thành bytes
              #print("encrypted_content:", encrypted_content)

              
  
              # Cập nhật text_area thành nội dung đã mã hóa (hiển thị dưới dạng string)
              text_area.delete("1.0", "end")  # Xóa hết nội dung cũ trong text_area
              text_area.insert("1.0", encrypted_content)  # Hiển thị nội dung mã hóa trong text_area

              default_ext = ".enc"
              content_to_write = encrypted_content  # Dữ liệu mã hóa dưới dạng chuỗi Base64 để lưu vào file
              file_types = [("Encrypted Files", "*.enc"), ("All Files", "*.*")]
          except Exception as e:
            messagebox.showerror("Mã hoá thất bại", f"Mã hoá thất bại: {e}")
            return current_file  # Nếu mã hóa thất bại, trả về current_file

        else:
          # Nếu không nhập key thì lưu file bình thường
          content_to_write = plaintext  # Sử dụng nội dung văn bản gốc
          default_ext = ".txt"
          file_types = [("Text Files", "*.txt"), ("All Files", "*.*")]  # Hộp thoại cho phép lưu file văn bản
        
        # Hiện hộp thoại file lưu vào Desktop
        current_file_path = filedialog.asksaveasfilename(defaultextension=default_ext,
                                                            filetypes=file_types, 
                                                            initialdir=str(Path.home() / "Desktop"))
            
        # Kiểm tra nếu người dùng không chọn file (hủy thao tác lưu)
        if not current_file_path:
          return current_file_path  # Nếu không có file_path (người dùng hủy thao tác), không tiếp tục lưu
        
      else:
        # Nếu file đã có, kiểm tra xem có phải là file mã hóa không
         if FileOperations.is_encrypted(current_file):  # Kiểm tra nếu file là file mã hóa
            # Gọi hàm handle_reencryption để yêu cầu mã hóa lại nếu là file đã mã hóa
            content_to_write = FileOperations.handle_reencryption(text_area.get("1.0", "end-1c"))
            if content_to_write is None:
              return current_file  # Nếu không muốn mã hóa lại, hủy thao tác
         
         else:
            # Save bình thường nếu không phải file mã hóa
              content_to_write = text_area.get("1.0", "end-1c")
              current_file_path = current_file  # Đặt đường dẫn cho file đã có
      try:
         # Kiểm tra nếu `current_file_path` chưa được gán (trường hợp Save As lần đầu)
          if not current_file_path:
            return current_file  # Nếu không có file_path, không thực hiện lưu

          # Lưu nội dung vào tệp dưới dạng chuỗi Base64
          with open(current_file_path, "w", encoding="utf-8") as file:
            file.write(content_to_write)

          return current_file_path  # Trả về đường dẫn của file đã lưu
      except Exception as e:
          messagebox.showerror("Lỗi lưu file", f"Lưu file thất bại: {e}")  # Nếu có lỗi khi lưu file
          return current_file  # Trả về current_file nếu có lỗi
      
    
    @staticmethod
    def handle_reencryption(content):
      confirm = messagebox.askyesno("Thông báo", "File này đã mã hoá. Bạn có muốn mã hoá lại không?")
      if confirm:
        # Yêu cầu nhập key mã hóa
        key = Dialogs.ask_ecryption_key()
        if key:
            try:
                # Mã hóa lại nội dung
                encryptor = AESEncryptor(key)
                encrypted_content = encryptor.encrypt(content.encode("utf-8"))  # Mã hóa nội dung dưới dạng bytes

                # Trả về nội dung mã hóa để lưu vào file (sau khi mã hóa thành công)
                return encrypted_content  # Trả về nội dung mã hóa 
            except Exception as e:
                Dialogs.show_ecryption_error()  # Hiển thị lỗi khi mã hóa thất bại
                return None  # Nếu có lỗi, trả về None
        else:
            messagebox.showwarning("Cảnh báo", "Bạn cần nhập khoá để mã hoá lại nội dung!")  # Nếu không nhập key
            return None
      else:
        return content  # Nếu người dùng không muốn mã hóa lại, giữ nguyên nội dung

        
      
    @staticmethod
    #mã hoá nội dung của file đã chọn và ghi đè
    def encrypt_and_overwrite_file(filepath: str, encryptor: AESEncryptor):
      try:
        with open(filepath, 'r', encoding='utf-8') as f:
            plaintext = f.read()
        
        # Chuyển sang byte trước khi mã hoá
        encrypted = encryptor.encrypt(plaintext.encode('utf-8'))
        
        # Ghi đè với chế độ nhị phân
        with open(filepath, 'wb') as f:
            f.write(encrypted)
      except Exception as e:
        print(f"[Lỗi] Không thể ghi đè file đã mã hoá: {e}")

        
    @staticmethod
    #mã hoá nội dung của file chỉ định bằng khoá được cung cấp
    def encrypt_external_file(filepath, key):
      try:
        encryptor = AESEncryptor(key)
        with open(filepath, 'rb') as f:
          original_data = f.read()
        
        encrypted_data =encryptor.encrypt(original_data) #string base64
      
        #chuyển string -> bytes trước khi ghi file nhị phân
        with open(filepath, 'wb') as f:
          f.write(encrypted_data.encode('utf-8'))
        return True
      except Exception as e:
        print(f"[Lỗi] Không thể mã hoá file: {e}")
        
    @staticmethod
    def decrypt_file(filepath: str, key: str, tab_control, text_widgets):
    #giải mã cho IP 1
      try:
        # Đọc nội dung file
        with open(filepath, 'r', encoding='utf-8') as file:
            encrypted_data = file.read().strip()

        # Tạo đối tượng giải mã và thực hiện giải mã
        decryptor = AESDecryptor(key)
        plaintext = decryptor.decrypt_data(encrypted_data)

        #lấy text widgets hiện tại 
        current_index = tab_control.index("current")
        text_area = text_widgets[current_index] if current_index < len(text_widgets) else None

        #hiện thị lên giao diện
        if text_area:
          text_area.delete("1.0",tk.END)
          text_area.insert("1.0", plaintext)
          
        # Ghi đè nội dung đã giải mã vào chính file đó
        """with open(filepath, 'w', encoding='utf-8') as file:
            file.write(plaintext)"""

        messagebox.showinfo("Success", "File đã được giải mã.")
      except Exception as e:
        messagebox.showerror("Error", f"Giải mã file thất bại: {e}")
        
    @staticmethod
    def decrypt_text_area(text_area, key: str):
    #giải mã cho IO 2
      try:
        # Lấy nội dung hiện tại trong text area
        encrypted_data = text_area.get("1.0", "end-1c")

        # Tạo đối tượng giải mã và thực hiện giải mã
        decryptor = AESDecryptor(key)
        plaintext = decryptor.decrypt_data(encrypted_data)

        # Xóa nội dung cũ và cập nhật nội dung đã giải mã
        text_area.delete("1.0", "end")
        text_area.insert("1.0", plaintext)

        messagebox.showinfo("Success", "Nội dung đã được giải mã và được cập nhật thành công.")
      except Exception as e:
        messagebox.showerror("Error", f"Giải mã nội dung thất bại: {e}")

    @staticmethod
    def is_encrypted(file_path):
      return os.path.splitext(file_path)[1].lower()== ".enc"