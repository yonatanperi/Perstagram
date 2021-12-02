from tkinter import *


class GUIForm:

    def __init__(self, client):
        self.root = Tk()
        self.root.geometry('470x600')
        self.root.title('Perstagram')
        self.client = client

    def go_to_page(self, page, *args):
        self.root.destroy()
        page(self.client, *args).run()

    def run(self):
        self.root.mainloop()
