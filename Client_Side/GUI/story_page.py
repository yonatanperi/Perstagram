from .app_form import AppForm
from tkinter import *
from tkinter.ttk import *
from PIL import ImageTk


class StoryPage(AppForm):

    def __init__(self, client):
        super().__init__(client, StoryPage)

        self.photos_stack = []
        self.story_image_generator = self.get_next_story_image()
        self.inline = []  # it's a queue!

        # create main frame
        main_frame = Frame(self.root)

        # username label
        self.username_lbl = Label(main_frame, text="Hit Next!", font=("Bebas", 12), anchor='w')
        self.username_lbl.grid(row=0, column=1, padx=10, pady=10)

        # navigation buttons
        Button(main_frame, text="Prev", command=self.prev_story).grid(row=1, column=0, padx=10, pady=10)
        Button(main_frame, text="Next", command=self.next_story).grid(row=1, column=2, padx=10, pady=10)

        self.image_lbl = Label(main_frame)
        self.image_lbl.grid(row=1, column=1, padx=10, pady=10)

        main_frame.pack()

    def next_story(self):
        try:
            next_story = self.inline.pop(0) if self.inline else next(self.story_image_generator)
            self.change_story_photo(*next_story)
        except StopIteration:
            self.username_lbl.configure(text=f"All Caught Up!")

    def prev_story(self):
        if len(self.photos_stack) > 1:
            current_story = self.photos_stack.pop()
            self.inline.append(current_story)
            self.change_story_photo(*self.photos_stack[-1])

    def change_story_photo(self, username: str, image: Image):
        # change username
        self.username_lbl.configure(text=f"@{username}")

        # change photo
        photo = ImageTk.PhotoImage(image)
        self.image_lbl.configure(image=photo)
        self.image_lbl.image = photo

        # insert to stack
        self.photos_stack.append((username, image))

    def get_next_story_image(self):
        """

        """
        for username in self.client.get_answer(("get interest users", self.client.get_answer(("get username", ))))[
            "following"]:
            stories_id = self.client.get_answer(("get stories", username))
            for story_id in stories_id:
                yield username, self.client.get_answer(("get story", username, story_id))
