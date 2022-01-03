from .app_form import AppForm
from .post_object import Post
from tkinter import *
from tkinter.ttk import *


class HomePage(AppForm):
    POST_NUMBER_LOAD_BUFFER = 3

    def __init__(self, client):
        super().__init__(client, self)

        self.seen_all_posts: bool = False
        self.top_bar_hight_ratio = 0.25  # the top part relative to one post
        self.scroll_frame = self.get_scrollbar_frame()
        self.current_post_index = 0
        self.posts = []

        Label(self.scroll_frame, text="perstagram", font=("Billabong", 40)).pack(pady=15, padx=10)

        # Pack initial posts
        for i in range(self.POST_NUMBER_LOAD_BUFFER):
            post = self.client.get_answer(("get next post", i + 1))  # username, post_id
            if post:
                self.posts.append(post)
                self.pack_post(*post)

    def analyze_location(self):
        """
        Check when the user viewed a frame.
        """
        # Now percentage_location will be set
        # The binomial for this problem is: (x + y - l) / (2 - 2 * l)
        # When x is the top of the scroll bar, y is the bottom and l is the length of it.

        # because l = y - x,
        # The binomial is: x / (1 - y + x)

        x, y = self.scrollbar.get()
        if x == 0 and y == 1:
            # no scroll region
            percentage_location = 1
        else:
            percentage_location = x / (1 - y + x)
        print(f"{percentage_location}, {(self.top_bar_hight_ratio + self.current_post_index + 1) / (self.top_bar_hight_ratio + len(self.posts))}")

        if percentage_location >= (self.top_bar_hight_ratio + self.current_post_index + 1) / (
                self.top_bar_hight_ratio + len(self.posts)) and self.current_post_index < len(self.posts):
            # don't even ask about the condition line
            # passed post
            self.client.send_message(("seen post", *self.posts[self.current_post_index]))

            if self.seen_all_posts:
                self.current_post_index += 1  # this is the only thing
            else:
                next_post = self.client.get_answer(("get next post", self.POST_NUMBER_LOAD_BUFFER))
                self.current_post_index += 1

                if next_post:
                    self.posts.append(next_post)
                    self.pack_post(*next_post)
                else:  # this happens ones
                    self.seen_all_posts = True
                    Label(self.scroll_frame, text="You're all caught up!", font=("Helvetica 14 bold", 18)).pack(
                        pady=15, padx=10,
                        fill='x',
                        expand=True)

    def pack_post(self, username, post_id):
        Post(self.client, username, post_id, self.scroll_frame).post_frame.pack(pady=10)
