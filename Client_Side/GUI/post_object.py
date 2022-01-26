from tkinter import *
from tkinter.ttk import *

from PIL import ImageTk


class Post:
    def __init__(self, client, username, post_id, root_frame):
        """
        create a post frame with all the information about it.
        :param client: the regular client
        :param username: the owner of the post
        :param post_id: just the post id
        """
        self.root = root_frame
        self.client = client
        self.username = username
        self.post_id = post_id
        self.post_data = self.client.get_answer(("get post", username, self.post_id))

        # Create A Post Frame
        self.post_frame = Frame(self.root)

        if self.post_data["image"] == "closed!":
            Label(self.post_frame, text=f"This user is closed!", font=("Helvetica 18 bold", 12)).pack(pady=15, padx=10)
        else:
            Label(self.post_frame, text=f"@{username}", font=("Bebas", 12), anchor='w').pack(pady=5, padx=10,
                                                                                             fill='both')

            photo = ImageTk.PhotoImage(self.post_data["image"])
            image_lbl = Label(self.post_frame, image=photo)
            image_lbl.image = photo
            image_lbl.pack(pady=10, padx=10)

            Label(self.post_frame, text=f"{len(self.post_data['likes'])} Likes!",
                  font=("Helvetica 18 bold", 10), anchor='w').pack(pady=5, padx=10, fill='both')

            opinion_frame = Frame(self.post_frame)

            # like button
            client_username = self.client.get_answer(("get username",))
            if client_username != username:
                button_text = "Dislike" if client_username in self.post_data['likes'] else "Like"
                Button(opinion_frame,
                       text=button_text,
                       command=lambda: self.client.send_message((button_text.lower(), username, post_id))).grid(row=0,
                                                                                                                column=0,
                                                                                                                padx=7)

            # view comments button
            Button(opinion_frame,
                   text="View Comments").grid(row=0, column=1, padx=7)  # TODO goto comments form

            opinion_frame.pack(pady=5, padx=10)
