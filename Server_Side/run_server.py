"""
listen to new clients and handles the connected ones.
"""

from threading import Thread
from client_object import Client
from lo_re import LoRe
from search import Search
from db_connection import SQL

import socket


class Server:

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []

    def start(self, ip, port):

        # set search object
        self.search_object = Search(SQL.ugly_list_2_list(SQL().get_all_usernames()))

        # starts listening to income clients
        self.server_socket.bind((ip, port))
        self.server_socket.listen(5)
        print(f"Server is listening on {ip} on port {port}")

        while True:
            client_socket = self.server_socket.accept()[0]
            print("Client connected!")
            Thread(target=LoRe(Client(client_socket, None), self).authenticate_client).start()

    def login(self, client):
        if client in self.clients:
            return False

        self.clients.append(client)
        print(f"{client} loged in!")
        return True


def main():
    server = Server()
    server.start("localhost", 1234)


if __name__ == '__main__':
    main()
