from .app_form import AppForm
from tkinter import *
from tkinter.ttk import *


class ProfilePage(AppForm):

    def __init__(self, client):
        super().__init__(client, self)
