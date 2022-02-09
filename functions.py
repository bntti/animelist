import string
from database import DB

ALLOWED_CHARACTERS = string.ascii_letters + string.digits + string.punctuation


def login(database: DB, username: str, password: str) -> list:
    errors = []
    if not database.user_exists(username):
        errors.append("Wrong username or password")
    elif not database.login(username, password):
        errors.append("Wrong username or password")
    return errors


def register(database: DB, username: str, password1: str, password2: str) -> list:
    errors = []

    if len(username) == 0:
        errors.append("Username can't be empty")
    elif len(username) > 64:
        errors.append("Username too long (max 64 characters)")
    if database.user_exists(username):
        errors.append("Username taken")
    for character in username:
        if character not in ALLOWED_CHARACTERS:
            errors.append(
                "Username may not contain whitespaces or non-ascii characters"
            )
            break

    if len(password1) == 0:
        errors.append("Password can't be empty")
    elif len(password1) > 64 or len(password2) > 64:
        errors.append("Password too long (max 64 characters)")
    if password1 != password2:
        errors.append("Passwords do not mach")

    return errors
