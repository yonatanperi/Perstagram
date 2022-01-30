from .smart_scroll_form import SmartScrollForm
from .tiny_user import TinyUser
from tkinter import *
from tkinter.ttk import *
from .search_page import SearchPage


class CloseFriendsPage(SmartScrollForm):

    def __init__(self, client):

        self.close_friends = client.get_answer(("get close friends",))

        super().__init__(client, 0.4, iter(self.close_friends), self.pack_user_card)

        # pack initial staff
        top_frame = Frame(self.scroll_frame)
        Label(self.scroll_frame, text="Close Friends", font=("Billabong", 30)).pack(pady=5)
        Button(self.scroll_frame, text="Add new friends",
               command=lambda: self.go_to_page(SearchPage, ("Add",),
                                               except_list=list(map(lambda t: t[0], self.close_friends)),
                                               full_button_command=lambda username: self.client.send_message(
                                                   ("add to close friends", username)),
                                               delete_when_clicked=True)).pack(pady=5)
        self.start_packing(top_frame)

    def pack_user_card(self, username: str):
        TinyUser(self.client, username, self.scroll_frame, False).tiny_user_frame.pack(fill=X)
