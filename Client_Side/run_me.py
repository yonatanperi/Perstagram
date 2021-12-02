from GUI.lo_re import LoRe
from client import Client


def main():
    client = Client()
    client.connect("localhost", 1234)

    LoRe(client).run()


if __name__ == '__main__':
    main()
