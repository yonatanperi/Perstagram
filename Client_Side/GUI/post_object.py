from tkinter import *
from tkinter.ttk import *

from PIL import ImageTk
from .comments_page import CommentsPage


class Post:
    def __init__(self, client, username, post_id, root_frame, go_to_page, HomePage):
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

            self.likes_label = Label(self.post_frame, text=f"{len(self.post_data['likes'])} Likes!",
                                     font=("Helvetica 18 bold", 10), anchor='w')
            self.likes_label.pack(pady=5, padx=10, fill='both')

            opinion_frame = Frame(self.post_frame)

            # like button
            client_username = self.client.get_answer(("get username",))
            if client_username != username:
                button_text = "Dislike" if client_username in self.post_data['likes'] else "Like"
                self.like_button = Button(opinion_frame, text=button_text, command=lambda: self.like(username, post_id))
                self.like_button.grid(row=0, column=0, padx=7)

            # view comments button
            Button(opinion_frame,
                   text="View Comments",
                   command=lambda: go_to_page(CommentsPage, username, post_id, HomePage)).grid(row=0, column=1, padx=7)

            opinion_frame.pack(pady=5, padx=10)

    def like(self, username, post_id):
        button_text = self.like_button["text"]
        self.client.send_message((button_text.lower(), username, post_id))
        likes = int(self.likes_label["text"][:-6])
        likes += 1 if button_text == "Like" else -1
        self.likes_label.config(text=f"{likes} Likes!")
        self.like_button.config(text="Dislike" if button_text == "Like" else "Like")
