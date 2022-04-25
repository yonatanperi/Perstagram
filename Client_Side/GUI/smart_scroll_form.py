from .app_form import AppForm
from tkinter import *
from tkinter.ttk import *


class SmartScrollForm(AppForm):

    def __init__(self, client, top_frame_hight_ratio: float, iterable_scrolling_items, pack_item_func,
                 seen_post: bool = False, bottom_lbl_text: bool = False,
                 item_load_number_buffer: int = 3):
        """
        Loads ITEM_LOAD_NUMBER_BUFFER items at first.
        When the user scrolls over an item's frame another gets loaded.
        :param client: the client
        :param top_frame_hight_ratio: most of the time, there is a widget at the top of the screen.
        This is the ratio of it relative to one item. must be less than 1.
        :param iterable_scrolling_items: an iterable object of the items.
        :param pack_item_func: The method which packs the items
        :param seen_post: just for the home page. send to the server "seen post" message.
        :param bottom_lbl_text: at the bottom, there is a label.
        """
        super().__init__(client, self)

        self.iterable_scrolling_items = iterable_scrolling_items
        self.top_bar_hight_ratio: float = top_frame_hight_ratio  # the top part relative to one post
        self.seen_post: bool = seen_post
        self.bottom_lbl_text = bottom_lbl_text
        self.scroll_frame = self.get_scrollbar_frame()
        self.pack_item = pack_item_func
        self.item_load_number_buffer = item_load_number_buffer

        self.seen_all_items: bool = False
        self.current_item_index = 0
        self.items = []

    def start_packing(self, top_frame):
        """
        Start the packing of the items
        :param top_frame: most of the time, there is a widget at the top of the screen.
        """
        top_frame.pack(pady=15)

        # Pack initial posts
        for index, item in enumerate(self.iterable_scrolling_items):
            if item:
                self.items.append(item)
                self.pack_item(*item)

            if index >= self.item_load_number_buffer - 1:
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

        # p(t) = int((m * (t - l) / (1 - l))) + 1
        # When: p - current_item
        # t - percentage_location
        # l - self.top_bar_hight_ratio
        # m - len(self.items)

        current_item = int(
            (len(self.items) * (percentage_location - self.top_bar_hight_ratio) / (1 - self.top_bar_hight_ratio))) + 1

        if current_item > self.current_item_index and self.current_item_index < len(self.items):
            # passed post
            if self.seen_post:
                self.client.send_message(("seen post", *self.items[self.current_item_index]))

            self.current_item_index += 1

            if not self.seen_all_items:
                try:
                    next_item = next(self.iterable_scrolling_items)
                    self.items.append(next_item)
                    self.pack_item(*next_item)

                except StopIteration:  # this happens ones
                    self.seen_all_items = True
                    if self.bottom_lbl_text:
                        Label(self.scroll_frame, text=self.bottom_lbl_text, font=("Helvetica 14 bold", 18)).pack(
                            pady=15,
                            fill='x',
                            expand=True)
