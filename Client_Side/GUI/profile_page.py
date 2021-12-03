from .app_form import AppForm
from tkinter import *
from tkinter.ttk import *


class ProfilePage(AppForm):

    def __init__(self, client, username=None):
        super().__init__(client, self)
        if not username:  # set default user
            self.username = client.send_message("get username")

        self.scroll_frame = self.get_scrollbar_frame()


