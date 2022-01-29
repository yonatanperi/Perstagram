from .smart_scroll_form import SmartScrollForm
from .tiny_user import TinyUser
from tkinter import *
from tkinter.ttk import *


class FollowRequestsPage(SmartScrollForm):

    def __init__(self, client):
        super().__init__(client, 0.3, iter(client.get_answer(("get follow requests",))), self.pack_user_card)

        self.tiny_user_frames = {}  # username: frame

        # pack initial staff
        top_frame = Frame(self.scroll_frame)
        Label(self.scroll_frame, text="Follow Requests", font=("Billabong", 30)).pack(pady=5)
        self.start_packing(top_frame)

    def pack_user_card(self, username: str):
        tiny_user_frame = TinyUser(self.client, username, self.scroll_frame, False, ("Admit",),
                                   full_button_command=lambda: self.admit(username)).tiny_user_frame
        self.tiny_user_frames[username] = tiny_user_frame
        tiny_user_frame.pack(fill=X)

    def admit(self, username):
        self.client.send_message(("admit", username))
        self.tiny_user_frames[username].pack_forget()
