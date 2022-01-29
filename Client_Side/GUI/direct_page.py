import os
from pathlib import Path
from .smart_scroll_form import SmartScrollForm
from .tiny_user import TinyUser
from tkinter import *
from tkinter.ttk import *
from .chat_page import ChatPage
from .search_page import SearchPage


class DirectPage(SmartScrollForm):

    def __init__(self, client):

        # create username folder in direct if not exists
        self.client_username = client.get_answer(("get username",))
        if self.client_username not in list(self.iterate_folder("direct")):
            os.mkdir(f"direct/{self.client_username}")

        # recv new messages
        new_messages = client.get_answer(("get direct messages",))
        self.new_message_usernames = []
        for message in new_messages:
            self.new_message_usernames.append(message[0])
            ChatPage.save_message_in_file_system(f"direct/{self.client_username}", message[0], True, *message[1:])

        super().__init__(client, 0.4, self.get_direct_users(), self.pack_user_card)

        # pack initial staff
        self.view_chat_button_options = ("View Chat", self.go_to_page, ChatPage)

        top_frame = Frame(self.scroll_frame)
        Label(self.scroll_frame, text="Direct", font=("Billabong", 30)).pack(pady=5)
        Button(self.scroll_frame, text="Start (new) Chat",
               command=lambda: self.go_to_page(SearchPage, self.view_chat_button_options)).pack(pady=5)
        self.start_packing(top_frame)

    def pack_user_card(self, username: str):

        tiny_user_frame = TinyUser(self.client, username, self.scroll_frame, False,
                                   self.view_chat_button_options).tiny_user_frame
        if username in self.new_message_usernames:
            Label(tiny_user_frame, text="NEW MESSAGES!!").grid(row=0, column=3)
        tiny_user_frame.pack(fill=X)

    def get_direct_users(self):
        """
        Checks the direct folder and reads the names of the text files.
        :return: a generator of the users in the filesystem
        """
        return iter(map(lambda a: (a,), self.iterate_folder(f"direct/{self.client_username}", -4)))

    @staticmethod
    def iterate_folder(path: str, final_path_cut: int = 0):
        """
        yields only the names of the files.
        :param path: the working path.
        :param final_path_cut: a possible to final cut of the name.
        """
        for p in Path(path).iterdir():
            p = str(p)
            yield p[len(path) + 1:final_path_cut] if final_path_cut else p[len(path) + 1:]
