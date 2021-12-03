from .app_form import AppForm
from tkinter import *
from tkinter.ttk import *


class HomePage(AppForm):

    def __init__(self, client):
        super().__init__(client, self)
        self.scroll_frame = self.get_scrollbar_frame()
        Label(self.scroll_frame, text="Welcome to PERSTAGRAM!", font=("Helvetica 18 bold", 25)).pack(pady=15, padx=10,
                                                                                                     fill='x',
                                                                                                     expand=True)

        for thing in range(100):
            Button(self.scroll_frame, text=f'Button {thing + 1} Yo!').pack(pady=10, padx=10, fill='x')
