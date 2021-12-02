from db_connection import SQL


class HandleUser:
    """
    After login, the user will send a lot of requests.
    This listener will handle them!
    """

    def __init__(self, client):
        self.client = client
        self.sql = SQL()

    def handle(self):
        recved = self.client.recv_message()  # structure: ["request", *args]

        if recved[0] == "post":
            self.sql.upload_image(self.client.username, recved[1], "posts")

        elif recved[0] == "post2story":
            self.sql.upload_image(self.client.username, recved[1], "stories")

        self.handle()
