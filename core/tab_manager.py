from tkinter import filedialog, messagebox, simpledialog
from core.file_operations import FileOperations
import tkinter as tk
from tkinter import ttk
import os
from core.encryption import AESEncryptor
from core.search.keywork_search import TFIDFKeywordSearcher


class TabManager:
  def __init__(self, tab_control, text_widgets, root):
    #lưu đối tượng tab_control (Notebook), danh sách text_widgets, và cửa sổ chính root
    self.tab_control = tab_control
    self.text_widgets = text_widgets
    self.root = root
    self.current_tab = 0 #index của tab hiện tại
    self.file_paths = []
    self.is_encrypted_list = []
    self.status_bar = None
    self.search_results = []
    self.current_result_index = -1
    self.on_result_select = []
    

    
    #gắn bind 1 lần duy nhất
    #self.tab_control.bind("<Button-1>", self.check_close_tab)
    

    self.find_window = tk.Toplevel(self.root)
    self.find_window.title("Find")
    self.find_window.geometry("300x50")
    self.find_window.withdraw()

    #tạo entry + nút trên find_window
    self.find_entry = tk.Entry(self.find_window)
    self.find_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
    self.find_button = tk.Button(self.find_window, text="Find", command=self.perform_search)
    self.find_button.pack(side=tk.LEFT, padx=5, pady=5)
    self.next_button = tk.Button(self.find_window, text="Next", command=self.goto_next_result)
    self.next_button.pack(side=tk.LEFT, padx=5, pady=5)

    #khởi tạo searcher
    self.tfidf_searcher = TFIDFKeywordSearcher(top_k=5)

  #tạo tab mới với tên file và vùng soạn thảo văn bản 
  def add_tab(self, filename="Untitled"):
    new_tab = ttk.Frame(self.tab_control)
    self.tab_control.add(new_tab, text=filename + " X")  # Tên tab kèm X
    self.tab_control.select(new_tab)

    text_area = tk.Text(new_tab, wrap=tk.WORD, bg="#1C2833", fg="white", background="#2C3E50")
    text_area.pack(expand=1, fill="both")
    #update_status_bar cập nhật ký tự
    text_area.bind("<KeyRelease>", lambda event: [self.update_status_bar(text_area), self.update_cursor_position(text_area)])
    #update_cursor_position cập nhật dòng và cột
    text_area.bind("<ButtonRelease>", lambda event: self.update_cursor_position(text_area))

    self.text_widgets.append(text_area)
    self.file_paths.append(None)
    self.current_tab = self.tab_control.index(new_tab)
    self.is_encrypted_list.append(False)

   
  def check_close_tab(self, event):
    try:
        clicked_index = self.tab_control.index(f"@{event.x},{event.y}")
    except Exception:
        return

    tab_id = self.tab_control.tabs()[clicked_index]
    tab_bbox = self.tab_control.bbox(clicked_index)
    if not tab_bbox:
        return

    x, y, width, height = tab_bbox
    tab_text = self.tab_control.tab(tab_id, "text")

    if width == 0 or height == 0:
       return

    print(f"tab_bbox = {tab_bbox}")
    # Tính toạ độ relative của click trong tab
    relative_x = event.x - x
    print(f"Click relative_x={relative_x}, width={width}, tab_text='{tab_text}'")

    # Kiểm tra nếu click ở vùng nút đóng (ví dụ 25px cuối tab)
    if relative_x >= width - 10 and tab_text.endswith("X"):
      self.close_tab(clicked_index)
    
            
            
  def close_tab(self, index):
    if 0 <= index < len(self.text_widgets):
        if len(self.text_widgets) > 1:
            self.tab_control.forget(index)
            del self.text_widgets[index]
            del self.file_paths[index]
        else:
            messagebox.showwarning("Thông báo", "Không thể đóng tab cuối cùng!")
      
      
  #Trả về text widget của tab hiện tại nếu tồn tại
  @staticmethod
  def get_current_text_widget(tab_control, text_widgets):
    try:
      current_index = tab_control.index("current")
      return text_widgets[current_index]
    except Exception:
      return None
  
  #gọi FileOperations đọc và hiển thị nội dung tong current_tab
  def open_file(self):
    file_path, content, is_encrypted = FileOperations.read_file()
    if file_path and content:
      current = self.get_current()
      if not current:
        self.add_tab()  # Hàm add_tab sẽ tạo một tab mới
        current = self.get_current()

      if current:
        current['text_widget'].delete("1.0", "end")
        current['text_widget'].insert("1.0", content)

        self.file_paths[current['index']] = file_path
        if current['index'] < len(self.is_encrypted_list):
          self.is_encrypted_list[current['index']] = is_encrypted
        else:
          self.is_encrypted_list.append(is_encrypted)
        
        self.root.title(f"Notepad Encryptor - {file_path}")

        #cập nhật tên tab
        short_name = os.path.basename(file_path)
        self.tab_control.tab(self.current_tab, text=short_name + " X")
        
  #lưu nội dung từ text widget của tab hiện tại ra file mới - không ghi đè file gốc
  def save_file(self, save_as=False):
    current = self.get_current()
    if not current:
      return
    
    text_area = current['text_widget']
    current_file = current['file_path']

    
    file_path = FileOperations.save_file(text_area, current_file, save_as=save_as)
    if file_path:
        if current['index'] >= len(self.file_paths):
          diff = current["index"] - len(self.file_paths) + 1
          self.file_paths.extend([None] * diff)
        self.file_paths[current['index']] = file_path

        short_name = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
        num_tabs = len(self.tab_control.tabs())
        if current['index'] < num_tabs:
          self.tab_control.tab(current['index'], text=short_name + " X")
        else:
          print(f"Warning: current_tab ({current['index']}) >= number of tabs ({num_tabs}), skipping tab update.")

        self.update_status_bar(text_area)
  
  #Cập nhật thanh trạng thái (status bar) với số lượng ký tự trong text
  def update_status_bar(self, text_area):
    try:
      if hasattr(text_area, "get") and callable(text_area.get):
        char_count = len(text_area.get("1.0", "end-1c"))
        if hasattr(self, 'character_label') and self.character_label:
          #cập nhật thanh trạng thái với số lượng ký tự 
          self.character_label.config(text=f"Character count: {char_count}")
      else:
        print("warning: invalid text widget passed to update_status_bar, skipping update.")
    except Exception:
      print("Error updating status bar")
    
  #mã hoá tab hiện tại
  def encrypt_current_tab(self):
    current_tab_index = self.get_current_tab_index()
    # kiểm tra tab hiện tại hợp lệ
    if current_tab_index < len(self.text_widgets):
      text_area = self.text_widgets[current_tab_index]
      file_path = self.file_paths[current_tab_index]
      #is_encrypted = self.is_encrypted_list[current_tab_index]
    else:
      messagebox.showerror("Lỗi", "Không tìm thấy tab hiện tại!")
      return
    #yêu cầu nhập khoá mã hoá
    key = simpledialog.askstring("Nhập key", "Vui lòng nhập key để mã hoá:", show='*')
    if not key:
      messagebox.showerror("Lỗi", "Bạn cần nhập key để mã hoá!")
      return
    
    #lấy nội dung văn bản đang soạn thảo
    plaintext = text_area.get("1.0", "end-1c").strip()
    if not plaintext:
      messagebox.showerror("Lỗi", "Không có nội dung để mã hoá!")
      return
    
    try:
      #khởi tạo đối tượng mã hoá với key được nhập
      encryptor = AESEncryptor(key)
      #mã hoá dữ liệu sau khi chuyển sang dạng bytes
      encrypted = encryptor.encrypt(plaintext.encode('utf-8'))

      
      
      file_path = filedialog.asksaveasfilename(defaultextension=".enc", filetypes=[("Encrypted Files", "*.enc"), ("All Files", "*.*")], 
                                                 initialfile=str(""))
        
      if not file_path:
        return
      #lưu đường dẫn file vào danh sách
      self.file_paths[current_tab_index] = file_path

      #lưu nội dung mã hoá vào file
      with open(file_path, "wb") as f:
        f.write(encrypted.encode('utf-8'))

      #cập nhật giao diện và thông báo thành công 
      text_area .delete("1.0", "end")
      text_area.insert("1.0", encrypted)

      #cập nhật trạng thái mã hoá cho tệp
      self.is_encrypted_list[current_tab_index] = True
      #thông báo thành công 
      messagebox.showinfo("Thành công", "Nội dung đã được mã hoá")
    except Exception as e:
      messagebox.showerror("Lỗi", f"Đã có lỗi xảy ra khi mã hoá: {e}")
  
  def get_current(self):
    index = self.get_current_tab_index()
    if index < len(self.text_widgets):
      text_widget = self.text_widgets[index]
      file_path = self.file_paths[index] if index < len(self.file_paths) else None
      is_encrypted = self.is_encrypted_list[index] if index < len(self.is_encrypted_list) else False
      return {
           "index": index,
           "text_widget": text_widget,
           "file_path": file_path,
           "is_encrypted": is_encrypted
        }
    return None

  def get_current_tab(self):
    current_tab_index = self.tab_control.index(self.tab_control.select())
    #kiểm tra chỉ số có còn hợp lệ không
    if current_tab_index < len(self.text_widgets):
      return self.text_widgets[current_tab_index]
    return None
  
  #trả về chỉ số của tab hiện tại
  def get_current_tab_index(self):
    return self.tab_control.index(self.tab_control.select())
  
  def show_find_bar(self):
    #kiểm tra nếu cửa sổ find_window đã tồn tại và chưa bị đóng
    if hasattr(self, 'find_window') and self.find_window.winfo_exists():
      self.find_window.deiconify()
    else:
      self.find_window = tk.Toplevel(self.root)
      self.find_window.title("Find")
      self.find_window.geometry("300x50")

      #thêm 2 nút find và next

      self.next_button = tk.Button(self.find_window, text="Next", command=self.goto_next_result)
      self.next_button.pack(side=tk.RIGHT, padx=5, pady=5)


      self.find_button = tk.Button(self.find_window, text="Find", command=self.perform_search)
      self.find_button.pack(side=tk.RIGHT, padx=5, pady=5)


      #tạo entry và đặt vị trí của nó
      self.find_entry = tk.Entry(self.find_window)
      self.find_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

    self.find_window.deiconify()
    self.find_window.grab_set()
    self.find_window.lift()
      
  def hide_find_bar(self):
    if hasattr(self, 'find_window') and self.find_window.winfo_exists():
      self.find_window.withdraw()
  
  def update_cursor_position(self, text_area):
    try:
      pos = text_area.index(tk.INSERT)
      line, col = pos.split('.')

      col = str(int(col) + 1)
      #cập nhật label dòng
      if hasattr(self, 'line_label') and self.line_label:
        self.line_label.config(text=f"Line: {line}")
      #cập nhật label cột
      if hasattr(self, 'column_label') and self.column_label:
        self.column_label.config(text=f"Column: {col}")
    except Exception:
      print("Error updating cursor position")
  

  #được gọi từ nút Find trong find_window
  def search_keyword(self, keyword: str):
    text_widget = self.get_current_text_widget()
    if not text_widget:
      return []
    
    full_text = text_widget.get("1.0", "end-1c")
    self.search_results = self.tfidf_searcher.search(keyword, full_text)

    if not self.search_results:
      messagebox.showinfo("Thông báo", "Không tìm thấy kết quả")
      return []
    
    self.current_result_index = 0
    self.goto_search_result(self.search_results[self.current_result_index])

    return self.search_results
  


  def goto_search_result(self, result):
    text_area = self.get_current_text_widget(self.tab_control, self.text_widgets)
    if not text_area:
      return
    
    #lấy số dòng = index + 1 (dòng bắt đầu từ 1)
    line = result['index'] + 1

    #xoá highlight cũ trên toàn bộ text_area
    text_area.tag_remove("search_highlight", "1.0", tk.END)
    text_area.tag_remove("bold_highlight", "1.0", tk.END)
    
    #tạo highlight cho dòng chứa kết quả
    start = f"{line}.0"
    end = f"{line}.end"
    text_area.tag_add("search_highlight", start, end)
    text_area.tag_config("search_highlight", background="gray")

    #đặt con trỏ đến kết quả
    text_area.mark_set(tk.INSERT, start)
    text_area.see(start)

  #khi nhấn next trong option find
  def goto_next_result(self):
    text_area = self.get_current_text_widget(self.tab_control, self.text_widgets)
    if not text_area or not self.search_results:
        return

    # Cập nhật chỉ số kết quả hiện tại
    self.current_result_index += 1
    if self.current_result_index >= len(self.search_results):
        self.current_result_index = 0  # quay lại đầu danh sách

    # Xóa highlight cũ trước khi thêm mới
    text_area.tag_remove("search_highlight", "1.0", tk.END)
    text_area.tag_remove("bold_highlight", "1.0", tk.END)

    # Lấy vị trí dòng kết quả (index + 1)
    line = self.search_results[self.current_result_index]['index'] + 1
    start = f"{line}.0"
    end = f"{line}.end"

    # Tạo highlight cho dòng chứa kết quả
    text_area.tag_add("search_highlight", start, end)
    text_area.tag_config("search_highlight", background="gray")

    #tô đậm kết quả vừa tìm dược
    text_area.tag_add("bold_highlight", start, end)
    text_area.tag_config("bold_highlight")


    # Đặt con trỏ tới đầu dòng và cuộn tới đó
    text_area.mark_set(tk.INSERT, start)
    text_area.see(start)
    
  #được gọi từ nút find trong find_window
  def perform_search(self):
    keyword = self.find_entry.get().strip()
    if not keyword:
        messagebox.showerror("Thông báo", "Vui lòng nhập từ khóa để tìm kiếm")
        return
    
    text_widget = self.get_current_text_widget(self.tab_control, self.text_widgets)
    if not text_widget:
        messagebox.showerror("Thông báo", "Không có nội dung để tìm kiếm")
        return
    
    full_text = text_widget.get("1.0", "end-1c")
    self.search_results = self.tfidf_searcher.search(keyword, full_text)
    self.current_result_index = 0

    if not self.search_results:
        messagebox.showinfo("Thông báo", "Không tìm thấy kết quả")
        return
    
    self.show_search_results_popup()

  #được gọi từ perform search
  def show_search_results_popup(self):
    if not self.search_results:
        messagebox.showinfo("Thông báo", "Không có kết quả để hiển thị")
        return
    
    if hasattr(self, 'search_results_popup') and self.search_results_popup.winfo_exists():
        self.search_results_popup.destroy()

    self.search_results_popup = tk.Toplevel(self.root)
    self.search_results_popup.title("Kết quả tìm kiếm")
    self.search_results_popup.geometry("400x300")

    self.search_listbox = tk.Listbox(self.search_results_popup)
    self.search_listbox.pack(expand=True, fill=tk.BOTH)
    
    #hiện thị các kết quả tìm kiếm
    for res in self.search_results:
      line_num = res['index'] + 1
      preview = res['text'][:50] + ("..." if len(res['text']) > 50 else "")
      self.search_listbox.insert(tk.END, f"Dòng {line_num}: {preview}")

    #mặt định cho lựa chọn kết quả đầu tiên
    self.search_listbox.select_set(0)
    self.search_listbox.activate(0)

    '''#nút Next
    btn_next = tk.Button(self.search_results_popup, text="Next", command=self.goto_next_result)
    btn_next.pack(pady=5)'''

    #nút Close
    btn_close = tk.Button(self.search_results_popup, text="Close", command=self.search_results_popup.destroy)
    btn_close.pack(pady=5)

    self.search_listbox.bind('<<ListboxSelect>>', self.on_result_select)
    # Hiển thị kết quả đầu tiên
    self.goto_search_result(self.search_results[self.current_result_index])

def on_result_select(self, event):
    print("on_result_select is called") 
    sel = self.search_listbox.curselection()
    if sel:  
        idx = sel[0]
        self.current_result_index = idx
        self.goto_search_result(self.search_results[idx])
        
    

    

   

    

    
