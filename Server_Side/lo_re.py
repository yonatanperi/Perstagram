import smtplib
from email.mime.text import MIMEText

from db_connection import SQL
from handle_user import HandleUser
from captcha.image import ImageCaptcha
from PIL import Image
import string
import random


class LoRe:
    RANDOM_TEXT_LENGTH = 1  # 7
    MAX_WRONG_TRIES = 3
    PERSTAGRAM_EMAIL_ADDESS = "perstagram.peri@gmail.com"

    def __init__(self, client, server):
        self.server = server
        self.client = client
        self.sql = SQL()

    def authenticate_client(self):
        """
        Log in or Register, server side.
        :return: Activates the HandleUser class when authenticated
        """

        # Captcha
        captcha_image, captcha_text = self.get_captcha_image()
        self.client.send_message(captcha_image)
        self.verify_user_text(captcha_text, self.authenticate_client)
        # Finished captcha!

        return self._really_authenticate_client()

    def _really_authenticate_client(self):
        """
        Log in or Register, server side.
        :return: Activates the HandleUser class when authenticated
        """

        # The client should send a message (a list) with the authentication's details
        authentication = self.client.recv_message()  # [username, password, *args]

        if authentication == "forgot password":
            self.forgot_password(self.client.recv_message())  # recv: email
            return self._really_authenticate_client()

        lo_re = self.sql.login  # we don't know yet if the user registered or loged in.
        args = []
        if len(authentication) > 2:  # When log in, the client sends 2 items in the list: username and password.
            lo_re = self.sql.register
            args.append(self.server.search_object)

        if not lo_re(*(list(authentication) + args)):  # authenticating in the sql
            self.client.send_message(False)
            return self._really_authenticate_client()

        self.client.send_message(True)
        self.client.username = authentication[0]

        # user authenticated!
        """
        if self.sql.get_user_type(self.client.username) == "admin":
            return AdminRoom(self.client, self.server).main_menu()
        """
        return HandleUser(self.client, self.server, LoRe).handle()

    def verify_user_text(self, code: str, dead_end_function):
        """
        Verifies a code with the user.
        :param code: the code.
        :param dead_end_function: when failed.
        :return: the dead_end_function.
        """
        authorised = False
        try_index = 0
        while not authorised:
            try_index += 1
            authorised = self.client.recv_message().upper() == code

            if try_index >= self.MAX_WRONG_TRIES and not authorised:
                self.client.send_message("code changed")
                return dead_end_function()

            self.client.send_message(authorised)

    def generate_random_string(self) -> str:
        return ''.join(random.choice(string.ascii_uppercase) for i in range(self.RANDOM_TEXT_LENGTH))

    def get_captcha_image(self) -> tuple:
        """
        Generate an image with captcha random text
        :return: tuple: (the image, the text)
        """
        # Create a random string, which will be the captcha text
        captcha_text = self.generate_random_string()

        # Create an image instance
        image = ImageCaptcha(width=210, height=68)  # Fixed size

        # generate the image of the given text
        return Image.open(image.generate(captcha_text)), captcha_text

    def forgot_password(self, users_email: str):
        """
        Send Email with code to the users_email
        """
        code = self.generate_random_string()
        msg = MIMEText(code)

        # me == the sender's email address
        # you == the recipient's email address
        me = self.PERSTAGRAM_EMAIL_ADDESS
        you = users_email

        msg['Subject'] = "Reset password - Perstagram"
        msg['From'] = me
        msg['To'] = you

        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        # send it via gmail
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        s.set_debuglevel(1)
        try:
            s.login(me, "732454545")
            s.sendmail(me, [you], msg.as_string())
        finally:
            s.quit()

        if not self.verify_user_text(code, self.forgot_password):  # for the recursion
            self.sql.replace_password(users_email, self.client.recv_message())
