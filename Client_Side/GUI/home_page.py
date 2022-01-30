from .smart_scroll_form import SmartScrollForm
from tkinter import *
from tkinter.ttk import *
from .post_object import Post


class HomePage(SmartScrollForm):

    def __init__(self, client):
        super().__init__(client, 0.4, self.posts_generator(),
                         lambda username, post_id: Post(self.client, username, post_id, self.scroll_frame,
                                                        self.go_to_page, HomePage).post_frame.pack(pady=10), True,
                         "You're all caught up!")

        top_frame = Frame(self.scroll_frame)
        Label(self.scroll_frame, text="perstagram", font=("Billabong", 40)).pack(pady=5)
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
                ("get next post", index if index <= self.item_load_number_buffer else self.item_load_number_buffer))
            if post:
                yield post
            else:  # when done, post will be None
                break
