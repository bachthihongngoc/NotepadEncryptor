import tkinter as tk
from ui.notepad import NotepadEncryptor

if __name__ == "__main__":
    root = tk.Tk()
    app = NotepadEncryptor(root)
    root.mainloop()
