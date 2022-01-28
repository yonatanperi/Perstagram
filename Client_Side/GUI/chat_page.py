import time
from datetime import datetime
from pathlib import Path
from threading import Thread

from .smart_scroll_form import SmartScrollForm
from .tiny_user import TinyUser
from tkinter import *
from tkinter.ttk import *
from .home_page import HomePage


class ChatPage(SmartScrollForm):
    SLEEP_BUFFER = 3
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, client, username):
        """
        Chat with a specific user.
        All the chat data is saves on the client side.
        :param username: the user to chat with.
        """
        super().__init__(client, 0.3, self.load_messages(), self.pack_message)

        # set main working path
        self.main_path = self.get_main_path(self.client)

        # define self.username
        self.username = username

        # pack initial staff
        top_frame = Frame(self.scroll_frame)
        TinyUser(self.client, username, self.scroll_frame, True).tiny_user_frame.pack(pady=5)
        self.start_packing(top_frame)

        # pack the message box to root
        self.message = StringVar()
        Entry(self.root, textvariable=self.message).pack(padx=40, pady=30, fill=X)
        Button(self.root, text="Send", command=self.send_message).pack(pady=10)

        # repack the bar frame
        self.bar_frame.pack_forget()
        new_bar_frame = Frame(self.root)
        new_bar_frame.pack(side="bottom", fill="x")
        Button(new_bar_frame, text="Back To Home Page", command=self.exit_chat).pack()

        # start chating
        self.recv_thread = Thread(target=self.recv_message)
        self.recv_thread.start()

    def send_message(self):
        message = self.message.get()
        self.message.set("")  # clear the entry
        now = datetime.now()

        # send to the other user
        self.client.send_message(("send direct message", self.username, message))

        # save in the file system
        self.save_message_in_file_system(self.main_path, self.username, False, now, message)

        # show on screen
        self.pack_message(False, now, message)

    def recv_message(self):
        new_messages = self.client.get_answer(("get specific direct messages", self.username))
        if new_messages == "done":  # the user has left the chat.
            return
        elif new_messages:  # something recved
            for new_message in new_messages:
                # save in the file system
                self.save_message_in_file_system(self.main_path, new_message[0], True, *new_message[1:])

                # show on screen
                self.pack_message(True, *new_message[1:])

        time.sleep(self.SLEEP_BUFFER)
        self.recv_message()

    def load_messages(self):
        """
        Checks the direct folder and reads the names of the text files.
        :return: a generator of the messages in tuple format: (message sender, date, the message)
                 message sender: False - our user sent it, True - the other user sent it.
        """
        try:
            # a generator of all the file's pathes
            with open(f"{self.main_path}\\{self.username}.txt", "r") as f:
                for line in f:
                    sender = bool(int(line[0]))
                    date = datetime.strptime(line[1:20], self.DATETIME_FORMAT)
                    message = line[20:-1]  # because of the \n
                    yield sender, date, message

        except FileNotFoundError:  # no prev messages
            pass

    def pack_user_card(self, username: str):
        TinyUser(self.client, username, self.scroll_frame, False,
                 ("View Chat", self.go_to_page, ChatPage)).tiny_user_frame.pack(fill=X)

    def pack_message(self, message_sender: bool, date: datetime, message: str):
        """
        Saves the message in the filesystem under the username folder
        :param message_sender: False - our user sent it, True - the other user sent it.
        :param date: the date of the message
        :param message: the actual message
        """
        if message_sender:
            anchor = NW
            background_color = "gray"
        else:
            anchor = NE
            background_color = "purple"

        Label(self.scroll_frame, text=message, background=background_color).pack(anchor=anchor, pady=5)

    def exit_chat(self):
        self.client.send_message(("done",))
        time.sleep(self.SLEEP_BUFFER + 1)
        self.go_to_page(HomePage)

    @staticmethod
    def save_message_in_file_system(main_path: str, username: str, message_sender: bool, date: datetime,
                                    message: str):
        """
        Saves the message in the filesystem under the username folder
        :param main_path: the working path
        :param username: the other user
        :param message_sender: False - our user sent it, True - the other user sent it.
        :param date: the date of the message
        :param message: the actual message
        """
        with open(Path(f"{main_path}\\{username}.txt"), "a") as f:
            f.write(f"{1 if message_sender else 0}{date.strftime(ChatPage.DATETIME_FORMAT)}{message}\n")

    @staticmethod
    def get_main_path(client):
        return f"direct\\{client.get_answer(('get username',))}"
