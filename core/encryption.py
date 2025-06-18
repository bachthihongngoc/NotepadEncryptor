from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import hashlib

class AESEncryptor:
    def __init__(self, key: str):
        # Tạo khóa AES 256-bit từ key người dùng nhập
        self.key = hashlib.sha256(key.encode()).digest()

    def pad(self, data: bytes) -> bytes:
        # Padding để dữ liệu là bội số của 16
        padding_len = 16 - (len(data) % 16)
        return data + bytes([padding_len] * padding_len)

    def unpad(self, data: bytes) -> bytes:
        padding_len = data[-1]
        return data[:-padding_len]

    def encrypt(self, data: bytes) -> str:
      iv = get_random_bytes(16)
      cipher = AES.new(self.key, AES.MODE_CBC, iv)
      padded_data = self.pad(data)
      ciphertext = cipher.encrypt(padded_data)
      encrypted_data = iv + ciphertext
      return base64.b64encode(encrypted_data).decode("utf-8")  # Trả về chuỗi base64


    def decrypt(self, data: bytes) -> bytes:
        # Giải mã dữ liệu bytes
        iv = data[:16]
        ciphertext = data[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        return self.unpad(decrypted)
    
    