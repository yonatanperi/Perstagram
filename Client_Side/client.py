import socket
import pickle
from encryption import Encrypt


class Client:
    HEADER_SIZE = 10
    BUFFER_SIZE = 16

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fernet = None  # define in connect func

    def connect(self, ip, port):
        self.client_socket.connect((ip, port))
        self.fernet = Encrypt(self.client_socket).get_symmetric_encryption_key()

    def recv_message(self):
        try:
            full_msg = b''
            msg_len = int(self.client_socket.recv(Client.HEADER_SIZE))
            if msg_len == 0:
                return
            buffer = Client.BUFFER_SIZE

            while len(full_msg) != msg_len:
                if msg_len - len(full_msg) < Client.BUFFER_SIZE:
                    buffer = msg_len - len(full_msg)
                msg = self.client_socket.recv(buffer)
                full_msg += msg

            # full msg recvd
            dec_message = pickle.loads(self.fernet.decrypt(full_msg))
            print("recved: " + str(dec_message))
            return dec_message
        except ConnectionResetError:  # loged out
            return

    def send_message(self, message):
        print("sent:" + str(message))
        bytes_enc_message = self.fernet.encrypt(pickle.dumps(message))
        self.client_socket.send(bytes(f'{len(bytes_enc_message):<{Client.HEADER_SIZE}}', 'utf-8') + bytes_enc_message)

    def get_answer(self, message):  # makes life easier
        self.send_message(message)
        return self.recv_message()
