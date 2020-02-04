from Crypto.Util.Padding import pad, unpad
import os, random, struct, base64
from Crypto.Cipher import AES


class AESCipher:

    def __init__(self, key):
        self.key = key

    def encrypt(self, raw):
        """加密"""
        raw = pad(raw.encode('utf-8'), 16)
        cipher = AES.new(self.key, AES.MODE_ECB)
        return base64.b64encode(cipher.encrypt(raw)) 

    def decrypt(self, enc):
        """解密"""
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_ECB)
        return unpad(cipher.decrypt(enc), 16).decode('utf-8')
    
    def encrypt_file(self, in_filename, out_filename, chunksize=64*1024):
        """加密文件"""
        if not out_filename:
            out_filename = in_filename + '.enc'
        
        cipher = AES.new(self.key, AES.MODE_ECB)
        filesize = os.path.getsize(in_filename)

        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                outfile.write(struct.pack('<Q', filesize))
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += ' ' * (16 - len(chunk) % 16)
                    outfile.write(cipher.encrypt(chunk))

    def decrypt_file(self, in_filename, out_filename=None, chunksize=24*1024):
        """解密文件"""
        if not out_filename:
            out_filename = os.path.splitext(in_filename)[0]

        with open(in_filename, 'rb') as infile:
            cipher = AES.new(self.key, AES.MODE_ECB)
            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(cipher.decrypt(chunk))

    def decrypt_body(self, body):
        """解密响应消息体"""
        cipher = AES.new(self.key, AES.MODE_ECB)
        return cipher.decrypt(body)
