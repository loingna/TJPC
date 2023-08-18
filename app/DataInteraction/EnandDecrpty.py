import base64
from Crypto.Cipher import AES


class EncryptDate:
    def __init__(self, key, iv):
        self.key = key.encode("utf-8")  # 初始化密钥
        self.iv = iv.encode("utf-8")  # 初始化偏移量
        self.length = 16  # 初始化数据块大小
        self.aes = AES.new(self.key, AES.MODE_CBC, self.iv)  # 初始化AES,CBC模式的实例
        # 截断函数，去除填充的字符
        self.unpad = lambda s: s[0:-s[-1]]

    def pad(self, text):
        """
        填充函数，使被加密数据的字节码长度是block_size的整数倍
        """
        count = len(text.encode('utf-8'))
        add = self.length - (count % self.length)
        entext = text + (chr(add) * add)
        return entext

    def encrypt(self, encrData):  # 加密函数
        a = self.pad(encrData)
        res = self.aes.encrypt(a.encode("utf-8"))
        msg = str(base64.b64encode(res), encoding="utf8")
        return msg

    def decrypt(self, decrData):  # 解密函数
        res = base64.decodebytes(decrData.encode("utf-8"))
        msg_text = self.aes.decrypt(res)
        decrypt_text = self.unpad(msg_text).decode('utf8')
        return decrypt_text


if __name__ == '__main__':
    aes_key = "1111111111111111"
    aes_iv = "9999999999999999"
    text_data = 'distrust'
    encrypt_data = EncryptDate(aes_key, aes_iv).encrypt(text_data)
    decrypt_data = EncryptDate(aes_key, aes_iv).decrypt(encrypt_data)
    print("原始数据:", text_data)
    print("加密后数据:", encrypt_data)
    print("数据解密:", decrypt_data)
