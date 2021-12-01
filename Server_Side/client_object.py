import time
import pickle
from encryption import Encrypt


class Client:
    HEADER_SIZE = 10
    BUFFER_SIZE = 16

    def __init__(self, client_socket, username):
        self.socket = client_socket
        self.username = username
        self.fernet = Encrypt(self.socket).get_symmetric_encryption_key()

    def recv_message(self):
        try:
            full_msg = b''
            new_msg = True
            msg_len = 0
            while len(full_msg) - Client.HEADER_SIZE != msg_len:
                msg = self.socket.recv(Client.BUFFER_SIZE)
                if new_msg:
                    msg_len = int(msg[:Client.HEADER_SIZE])
                    new_msg = False

                full_msg += msg

            # full msg recvd
            dec_message = pickle.loads(self.fernet.decrypt(full_msg[Client.HEADER_SIZE:]))
            print("recved: " + str(dec_message))
            return dec_message
        except ConnectionResetError:  # loged out
            return

    def send_message(self, message):
        print("sent:" + str(message))
        time.sleep(0.5)  # for the client to activate all the funcs
        bytes_enc_message = self.fernet.encrypt(pickle.dumps(message))
        self.socket.send(bytes(f'{len(bytes_enc_message):<{Client.HEADER_SIZE}}', 'utf-8') + bytes_enc_message)

    def get_answer(self, message):  # makes life easier
        self.send_message(message)
        return self.recv_message()

    def __eq__(self, other):
        return self.username == other.username

    def __str__(self):
        return self.username

    def __hash__(self):
        return self.username.__hash__()

    def __copy__(self):
        return Client(self.socket, self.username)

    __repr__ = __str__
