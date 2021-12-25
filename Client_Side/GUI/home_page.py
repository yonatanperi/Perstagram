from .app_form import AppForm
from .post_object import Post
from tkinter import *
from tkinter.ttk import *


class HomePage(AppForm):

    POST_NUMBER_LOAD_BUFFER = 5

    def __init__(self, client):
        super().__init__(client, self)
        self.scroll_frame = self.get_scrollbar_frame()
        Label(self.scroll_frame, text="Welcome to PERSTAGRAM!", font=("Helvetica 18 bold", 25)).pack(pady=15, padx=10,
                                                                                                     fill='x',
                                                                                                     expand=True)

        posts = self.client.get_answer(("get home page posts", self.POST_NUMBER_LOAD_BUFFER))  # username, post_id

        for post in posts:
            Post(self.client, post[0], post[1], self.scroll_frame).post_frame.pack(pady=10)

