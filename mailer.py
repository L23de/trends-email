import yagmail
import os
from dotenv import load_dotenv
load_dotenv()


class Mailer():
    email = os.environ.get("email")
    password = os.environ.get("password")
    receiver = os.environ.get("recv")
    message = """
        Hello world! 
        - Sent from Python
    """

    yag = yagmail.SMTP(email, password)
    yag.send(contents = message)
    