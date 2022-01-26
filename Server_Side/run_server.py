"""
listen to new clients and handles the connected ones.
"""

from threading import Thread
from client_object import Client
from lo_re import LoRe
from search import Search
from db_connection import SQL
from image_classification import ImageClassification

import socket


class Server:

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, ip, port):

        # set search object
        self.search_object = Search(SQL().get_all_usernames())
        self.classify_image = ImageClassification().classify

        # starts listening to income clients
        self.server_socket.bind((ip, port))
        self.server_socket.listen(5)
        print(f"Server is listening on {ip} on port {port}")

        while True:
            client_socket = self.server_socket.accept()[0]
            print("Client connected!")
            Thread(target=LoRe(Client(client_socket, None), self).authenticate_client).start()


def main():
    server = Server()
    server.start("localhost", 1234)


if __name__ == '__main__':
    main()
