from PIL import ImageTk

from .smart_scroll_form import SmartScrollForm
from tkinter import *
from tkinter.ttk import *


class CommentsPage(SmartScrollForm):

    def __init__(self, client, username, post_id, HomePage):
        """

        """
        post_data = client.get_answer(("get post", username, post_id))
        super().__init__(client, 10, iter(post_data["comments"]), self.pack_comment, item_load_number_buffer=20)

        # define staff
        self.username = username
        self.post_id = post_id

        # pack initial staff
        top_frame = Frame(self.scroll_frame)
        photo = ImageTk.PhotoImage(post_data["image"])
        image_lbl = Label(top_frame, image=photo)
        image_lbl.image = photo
        image_lbl.pack(pady=20)
        self.start_packing(top_frame)

        # pack the message box to root
        self.comment_text = StringVar()
        Entry(self.root, textvariable=self.comment_text).pack(padx=40, pady=30, fill=X)
        Button(self.root, text="Comment", command=self.comment).pack(pady=10)

        # repack the bar frame
        self.bar_frame.pack_forget()
        new_bar_frame = Frame(self.root)
        new_bar_frame.pack(side="bottom", fill="x")
        Button(new_bar_frame, text="Back To Home Page", command=lambda: self.go_to_page(HomePage)).pack()

    def comment(self):
        comment_text = self.comment_text.get()
        self.pack_comment(self.client.get_answer(("get username",)), comment_text)
        self.client.send_message(("comment", self.username, self.post_id, comment_text))
        self.comment_text.set("")

    def pack_comment(self, username: str, comment: str):
        """

        """
        Label(self.scroll_frame, text=f"{username}: {comment}").pack(pady=5)
