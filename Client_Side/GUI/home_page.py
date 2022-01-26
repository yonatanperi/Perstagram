from .smart_scroll_form import SmartScrollForm
from tkinter import *
from tkinter.ttk import *


class HomePage(SmartScrollForm):

    def __init__(self, client):
        super().__init__(client, 0.4, self.posts_generator(), True, "You're all caught up!")

        top_frame = Frame(self.scroll_frame)
        Label(self.scroll_frame, text="perstagram", font=("Billabong", 40)).pack(pady=5)
        # TODO stories

        self.start_packing(top_frame)

    def posts_generator(self):
        """
        A generator of the (username, post_id)'s of all posts.
        Simply asking the server each time.
        """
        index = 0
        while True:
            index += 1
            post = self.client.get_answer(
                ("get next post", index if index <= self.ITEM_LOAD_NUMBER_BUFFER else self.ITEM_LOAD_NUMBER_BUFFER))
            if post:
                yield post
            else:  # when done, post will be None
                break
