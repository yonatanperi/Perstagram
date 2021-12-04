from tkinter import *
from tkinter.ttk import *

from PIL import ImageTk


class Post:
    def __init__(self, client, username, post_id, root):
        """
        create a post frame with all the information about it.
        :param client: the regular client
        :param username: the owner of the post
        :param post_id: just the post id
        """
        self.root = root
        self.client = client
        self.username = username
        self.post_id = post_id
        self.post_data = self.client.get_answer(("get post", username, self.post_id))

        # Create A Post Frame
        self.post_frame = Frame(self.root)

        Label(self.post_frame, text=f"@{username}", font=("Helvetica 18 bold", 12)).pack(pady=15, padx=10)

        photo = ImageTk.PhotoImage(self.post_data["image"])
        image_lbl = Label(self.post_frame, image=photo)
        image_lbl.image = photo
        image_lbl.pack(pady=10, padx=10)

        Label(self.post_frame, text=f"{len(self.post_data['likes'])} Likes!",
              font=("Helvetica 18 bold", 8)).pack(pady=15, padx=10)
