import string
from database import DB

ALLOWED_CHARACTERS = string.ascii_letters + string.digits + string.punctuation


def login(database: DB, username: str, password: str) -> str:
    if not database.user_exists(username):
        return "Wrong username or password"
    if not database.login(username, password):
        return "Wrong username or password"
    return "OK"


def register(database: DB, username: str, password1: str, password2: str) -> str:
    if len(username) == 0:
        return "Username can't be empty"
    if len(username) > 64:
        return "Username too long (max 64 characters)"
    for character in username:
        if character not in ALLOWED_CHARACTERS:
            return "Username may not contain whitespaces or non-ascii characters"
    if len(password1) > 64 or len(password2) > 64:
        return "Password too long (max 64 characters)"
    if password1 != password2:
        return "Passwords do not mach"
    if len(password1) == 0:
        return "Password can't be empty"
    if database.user_exists(username):
        return "Username taken"
    return "OK"
