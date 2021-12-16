"""
The server is doing the actual search.
This page is just presents the information.
"""

from .app_form import AppForm
from tkinter import *
from tkinter.ttk import *


class HomePage(AppForm):

    def __init__(self, client):
        super().__init__(client, self)
        self.scroll_frame = self.get_scrollbar_frame()