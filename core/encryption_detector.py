import os
from core.decryption import AESDecryptor

class EncryptionDetector:

  @staticmethod
  def is_file_encrypted(filepath: str) -> bool:
    #kiểm tra file có phải là file mã hoá không dựa trên đuôi file
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".enc":
      return True
    return False
  
  @staticmethod
  def try_decrypt_content(content: str, key: str) -> str:
    decryptor = AESDecryptor(key)
    return decryptor.decrypt_data(content)
    
