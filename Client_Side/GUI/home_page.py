from .app_form import AppForm
from .post_object import Post
from tkinter import *
from tkinter.ttk import *


class HomePage(AppForm):
    POST_NUMBER_LOAD_BUFFER = 3

    def __init__(self, client):
        super().__init__(client, self)

        self.seen_all_posts: bool = False
        self.scroll_frame = self.get_scrollbar_frame()
        self.bottom_scroll_bar_percentage = 0  # Will be defined later
        self.current_post_index = 1
        self.posts = []

        # Pack initial posts
        for i in range(self.POST_NUMBER_LOAD_BUFFER):
            post = self.client.get_answer(("get next post", i + 1))  # username, post_id
            if post:
                self.posts.append(post)
                self.pack_post(*post)

        # set self.bottom_scroll_bar_percentage
        self.root.after(1000, self.set_bottom_scroll_bar_percentage)

    def set_bottom_scroll_bar_percentage(self):
        """
        The self.scrollbar.get()[1] is the location of the bottom part of the scrollbar.
        This function sets to self.bottom_scroll_bar_percentage its initial location.
        """
        location = self.scrollbar.get()
        self.bottom_scroll_bar_percentage = location[1] - location[0]

    def analyze_location(self):
        """
        Check when the user viewed a frame.
        """

        if self.bottom_scroll_bar_percentage == 1:  # no scroll regen
            percentage_location = 1
        else:
            percentage_location = self.scrollbar.get()[1] / (1 - self.bottom_scroll_bar_percentage)

        if percentage_location >= self.current_post_index / len(self.posts) and self.current_post_index < len(
                self.posts):
            # passed post
            print("passed post!")
            self.client.send_message(("seen post", *self.posts[self.current_post_index - 1]))

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
                    Label(self.scroll_frame, text="You're all caught up!", font=("Helvetica 14 bold", 25)).pack(
                        pady=15, padx=10,
                        fill='x',
                        expand=True)

    def pack_post(self, username, post_id):
        Post(self.client, username, post_id, self.scroll_frame).post_frame.pack(pady=10)
