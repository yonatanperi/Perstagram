"""
The server is doing the actual search.
This page is just presents the information.
There is no search button! the search is immediate!
"""
from typing import List
from .app_form import AppForm
from tkinter import *
from tkinter.ttk import *
from PIL import ImageTk

from .profile_page import ProfilePage


class SearchPage(AppForm):

    def __init__(self, client):
        super().__init__(client, self)

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
        row_index = 0

        for result in usernames:
            # result frame
            current_frame = Frame(self.scroll_frame)
            self.results_frames.append(current_frame)
            current_frame.pack(fill=X)

            # profile photo
            profile_photo = ImageTk.PhotoImage(
                self.client.get_answer(("get profile photo", result)))  # TODO put this in thread
            profile_photo_lbl = Label(current_frame, image=profile_photo)
            profile_photo_lbl.image = profile_photo
            profile_photo_lbl.grid(row=row_index, column=0, padx=10, pady=20)

            # username
            Label(current_frame, text=f"@{result}").grid(row=row_index, column=1, padx=10)

            # View profile button
            Button(current_frame, text="View profile", command=lambda m=result: self.go_to_page(ProfilePage, m)) \
                .grid(row=row_index, column=2, padx=50)

            row_index += 1
