from db_connection import SQL


class LoRe:

    def __init__(self, client, server):
        self.server = server
        self.client = client
        self.sql = SQL()

    def authenticate_client(self):

        authentication = self.client.recv_message()  # [username, password, *args]
        lo_re = self.sql.login
        if len(authentication) > 2:
            lo_re = self.sql.register

        if not lo_re(*authentication):
            self.client.send_message(False)
            return self.authenticate_client()

        self.client.username = authentication[0]
        if not self.server.login(self.client):
            self.client.send_message(False)
            return self.authenticate_client()

        self.client.send_message(True)

        # user authenticated!
        """
        if self.sql.get_user_type(self.client.username) == "admin":
            return AdminRoom(self.client, self.server).main_menu()
        """
        print("authenticated!")
        return