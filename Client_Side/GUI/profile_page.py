from .app_form import AppForm
from .post_object import Post
from tkinter import *
from tkinter.ttk import *


class ProfilePage(AppForm):

    def __init__(self, client, username=None):
        super().__init__(client, self)
        if not username:  # set default username
            self.username = client.get_answer(("get username",))
        else:
            self.username = username

        self.scroll_frame = self.get_scrollbar_frame()
        # About bar
        about_frame = Frame(self.scroll_frame)
        about_frame.pack()
        # TODO

        # All the user's posts
        self.posts_ids = self.client.get_answer(("get all posts", self.username))
        for post_id in self.posts_ids:
            Post(self.client, self.username, post_id[0], self.scroll_frame).post_frame.pack()
