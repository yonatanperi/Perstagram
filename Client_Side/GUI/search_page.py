"""
The server is doing the actual search.
This page is just presents the information.
There is no search button! the search is immediate!
"""
from typing import List
from .app_form import AppForm
from tkinter import *
from tkinter.ttk import *
from .tiny_user import TinyUser


class SearchPage(AppForm):

    def __init__(self, client, button_options: tuple = None, full_button_command=None, except_list=None,
                 delete_when_clicked: bool = False):
        """

        :param client:
        :param button_options: a tuple of: (text, page to go when clicked)
        :param full_button_command: to preform an entire method
        :param except_list: Won't show these results
        :param delete_when_clicked: Grid forget the button when clicked
        """
        super().__init__(client, self)

        if except_list is None:
            except_list = []

        self.except_list = except_list
        if button_options:
            button_options = list(button_options)
            if len(button_options) > 1:
                button_options[1] = self.go_to_page  # to make sure the go_to_page_function is correct
            self.button_options = button_options
        else:  # default is view profile
            from .profile_page import ProfilePage
            self.button_options = ProfilePage.get_view_profile_button_options(self.go_to_page)
        self.full_button_command = full_button_command
        self.delete_when_clicked = delete_when_clicked

        self.results_frames = []

        # Search box

        # Create a main frame
        main_frame = Frame(self.root)
        main_frame.pack(fill=X)

        Label(main_frame, text="Enter username: ").grid(row=0, column=0, padx=18, pady=10)
        self.username_path = StringVar()
        Entry(main_frame, textvariable=self.username_path, width=50).grid(row=0, column=1)
        self.username_path.trace("w", lambda name, index, mode: self.show_results(
            self.client.get_answer(("search", self.username_path.get()))
        ))

        self.scroll_frame = self.get_scrollbar_frame()

    def show_results(self, usernames: List[str]):
        """
        recv the needed info about the usernames and screen it.
        :param usernames:
        """
        # remove prev results
        for frame in self.results_frames:
            frame.pack_forget()

        # show new results
        self.results_frames = []

        for result in usernames:
            # result frame
            if result not in self.except_list:
                tiny_user = TinyUser(self.client, result, self.scroll_frame, False, self.button_options,
                                     full_button_command=self.full_button_command)
                current_frame = tiny_user.tiny_user_frame
                if self.delete_when_clicked:
                    tiny_user.button.config(
                        command=lambda t=tiny_user: [t.button_command(), t.tiny_user_frame.pack_forget()])
                    self.except_list.append(result)  # to not show again

                self.results_frames.append(current_frame)
                current_frame.pack(fill=X)
