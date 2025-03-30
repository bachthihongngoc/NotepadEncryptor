import tkinter as tk
from tkinter import filedialog, messagebox

class FileOperations:
    def __init__(self):
        pass

    def new_file(self, text_area, root):
        text_area.delete("1.0", tk.END)
        root.title("Notepad Encryptor - New File")
        return ""  # reset file path

    def open_file(self, text_area, root):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                text_area.delete("1.0", tk.END)
                text_area.insert(tk.END, content)
                root.title(f"Notepad Encryptor - {file_path}")
                return file_path
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open file:\n{str(e)}")
        return None

    def save_file(self, text_area, current_file, save_as=False):
        if save_as or not current_file:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt", 
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if not file_path:
                return current_file
            current_file = file_path
        else:
            file_path = current_file

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))
            return file_path
        except Exception as e:
            messagebox.showerror("Error", f"Cannot save file:\n{str(e)}")
            return current_file
