from Crypto.Cipher import AES
import base64
import hashlib

class FileEncryptor:
    def __init__(self, key):
        self.key = self._derive_key(key)

    def _derive_key(self, key):
        return hashlib.sha256(key.encode()).digest()

    def encrypt_text(self, text):
        cipher = AES.new(self.key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(text.encode())
        return cipher.nonce + tag + ciphertext

    def decrypt_text(self, encrypted_data):
        nonce = encrypted_data[:16]
        tag = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]
        
        cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()
