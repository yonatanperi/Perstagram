from tkinter import *


class GUIForm:

    def __init__(self, client):
        self.root = Tk()
        self.root.geometry('809x500')
        self.root.title('Perstagram')
        self.client = client
