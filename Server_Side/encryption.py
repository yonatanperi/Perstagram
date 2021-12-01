import rsa
import pickle
from cryptography.fernet import Fernet


class Encrypt:
    """
    Server Encrypt class
    """

    def __init__(self, socket):
        self.socket = socket

    def get_symmetric_encryption_key(self):
        # Asymmetric-key Encryption:
        public_key, private_key = rsa.newkeys(512)  # 512 bytes long
        # server goes first
        self.socket.send(pickle.dumps(public_key))
        enc_symmetric_key = self.socket.recv(64)
        symmetric_key = rsa.decrypt(enc_symmetric_key, private_key).decode()
        return Fernet(symmetric_key.encode())  # Symmetric-key Encryption:
