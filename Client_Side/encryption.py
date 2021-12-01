import rsa
import pickle
from cryptography.fernet import Fernet


class Encrypt:
    """
    Client Encrypt class
    """
    def __init__(self, socket):
        self.socket = socket

    def get_symmetric_encryption_key(self):
        # Symmetric-key Encryption:
        symmetric_key = Fernet.generate_key()

        # Asymmetric-key Encryption:
        # get public key
        public_key = pickle.loads(self.socket.recv(114))  # 114 because of the pickle
        enc_symmetric_key = rsa.encrypt(symmetric_key, public_key)  # 64 bytes long
        self.socket.send(enc_symmetric_key)

        return Fernet(symmetric_key)
