from tkinter import simpledialog, messagebox

class Dialogs:
    @staticmethod
    def   ask_decryption_key():
        return simpledialog.askstring("Nhập khoá", "File này đã mã hoá. Vui lòng nhập khoá để giải mã:", show="*")
    
    @staticmethod
    def   ask_ecryption_key():
        return simpledialog.askstring("Nhập khoá", "Nhập khoá để mã hoá:", show="*")

    @staticmethod
    def show_decryption_error(error):
        messagebox.showerror("Lỗi giải mã", f"Không thể giải mã file: {error}")
    
    @staticmethod
    def show_ecryption_error(error):
        messagebox.showerror("Lỗi giải mã", f"Không thể giải mã file: {error}")

    @staticmethod
    def show_open_file_error(error):
        messagebox.showerror("Lỗi mở file", f"Lỗi khi mở file: {error}")

    @staticmethod
    def prompt_for_key_encrypt(round_number=1):
      return simpledialog.askstring(
        "Nhập khoá", 
        f"Vui lòng nhập khoá để mã hoá:", 
        show="*"
    )

    @staticmethod
    def show_wrong_decryption_key():
        messagebox.showerror("Lỗi giải mã", "Khoá giải mã không chính xác.")
