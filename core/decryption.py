from Crypto.Cipher import AES
import base64
import hashlib
from tkinter import messagebox

class AESDecryptor:
    def __init__(self, key: str):
        """
        Khởi tạo đối tượng AESDecryptor với khóa được cung cấp.
        Khóa sẽ được chuyển đổi thành SHA-256 để phù hợp với AES-256.
        :param key: Khóa giải mã dưới dạng chuỗi.
        """
        self.key = hashlib.sha256(key.encode()).digest()  # Tạo khóa AES 256-bit từ key người dùng nhập

    def unpad(self, data: bytes) -> bytes:
        """
        Loại bỏ padding khỏi dữ liệu đã giải mã.
        :param data: Dữ liệu bytes đã giải mã.
        :return: Dữ liệu sau khi loại bỏ padding.
        """
        padding_len = data[-1]
        return data[:-padding_len]

    def decrypt_data(self, encrypted_data: str) -> str:
        """
        Giải mã dữ liệu được mã hóa bằng AES (CBC mode).
        :param encrypted_data: Chuỗi Base64 chứa IV + ciphertext.
        :return: Chuỗi dữ liệu đã giải mã (plaintext).
        """
        try:
            # Giải mã Base64 để lấy IV và ciphertext
            encrypted_bytes = base64.b64decode(encrypted_data)
            iv = encrypted_bytes[:16]  # IV chiếm 16 byte đầu tiên
            ciphertext = encrypted_bytes[16:]  # Phần còn lại là ciphertext

            # Tạo cipher AES ở chế độ CBC với IV
            cipher = AES.new(self.key, AES.MODE_CBC, iv)

            # Giải mã và loại bỏ padding
            decrypted_bytes = cipher.decrypt(ciphertext)
            plaintext = self.unpad(decrypted_bytes).decode('utf-8')

            return plaintext
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")