from .scroll_posts_frame import ScrollPostsFrame
from tkinter import *
from tkinter.ttk import *


class HomePage(ScrollPostsFrame):

    def __init__(self, client):
        super().__init__(client, 0.4, self.posts_generator(), True, "You're all caught up!")

        top_frame = Label(self.scroll_frame, text="perstagram", font=("Billabong", 40))
        self.start_packing(top_frame)

    def posts_generator(self):
        index = 0
        while True:
            index += 1
            post = self.client.get_answer(
                ("get next post", index if index <= self.POST_NUMBER_LOAD_BUFFER else self.POST_NUMBER_LOAD_BUFFER))
            if post:
                yield post
            else:  # when done, post will be None
                break
