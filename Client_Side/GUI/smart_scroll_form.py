from .app_form import AppForm
from .post_object import Post
from tkinter import *
from tkinter.ttk import *


class SmartScrollForm(AppForm):
    ITEM_LOAD_NUMBER_BUFFER = 3

    def __init__(self, client, top_frame_hight_ratio: float, iterable_scrolling_items, seen_post=False,
                 bottom_lbl_text=False):
        """
        Loads ITEM_LOAD_NUMBER_BUFFER items at first.
        When the user scrolls over an item's frame another gets loaded.
        :param client: the client
        :param top_frame_hight_ratio: most of the time, there is a widget at the top of the screen.
        This is the ratio of it relative to one item.
        :param iterable_scrolling_items: an iterable object of the items.
        :param seen_post: just for the home page. send to the server "seen post" message.
        :param bottom_lbl_text: at the bottom, there is a label.
        """
        super().__init__(client, self)

        self.iterable_scrolling_items = iterable_scrolling_items
        self.top_bar_hight_ratio: float = top_frame_hight_ratio  # the top part relative to one post
        self.seen_post: bool = seen_post
        self.bottom_lbl_text = bottom_lbl_text
        self.scroll_frame = self.get_scrollbar_frame()

        self.seen_all_posts: bool = False
        self.current_post_index = 0
        self.posts = []

    def start_packing(self, top_frame):
        """
        Start the packing of the items
        :param top_frame: most of the time, there is a widget at the top of the screen.
        """
        top_frame.pack(pady=15)

        # Pack initial posts
        for index, post in enumerate(self.iterable_scrolling_items):
            if post:
                self.posts.append(post)
                self.pack_post(*post)  # TODO ask in the init for the function which does this.

            if index >= self.ITEM_LOAD_NUMBER_BUFFER - 1:
                break

    def analyze_location(self):
        """
        Activated when the user scrolls.
        Checks if the user viewed a frame.
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

        if percentage_location >= (self.top_bar_hight_ratio + self.current_post_index + 1) / (
                self.top_bar_hight_ratio + len(self.posts)) and self.current_post_index < len(self.posts):
            # don't even ask about the condition line
            # passed post
            if self.seen_post:
                self.client.send_message(("seen post", *self.posts[self.current_post_index]))

            self.current_post_index += 1

            if not self.seen_all_posts:
                try:
                    next_post = next(self.iterable_scrolling_items)
                    self.posts.append(next_post)
                    self.pack_post(*next_post)

                except StopIteration:  # this happens ones
                    self.seen_all_posts = True
                    if self.bottom_lbl_text:
                        Label(self.scroll_frame, text=self.bottom_lbl_text, font=("Helvetica 14 bold", 18)).pack(
                            pady=15,
                            fill='x',
                            expand=True)

    def pack_post(self, username, post_id):
        Post(self.client, username, post_id, self.scroll_frame).post_frame.pack(pady=10)
