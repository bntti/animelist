import string
from secrets import token_hex

from flask import abort, session
from werkzeug.wrappers.response import Response

from repositories import user_repository


def logout() -> None:
    session.pop("username", None)
    session.pop("user_id", None)
    session.pop("show_hidden", None)
    session.pop("csrf_token", None)


def check_user() -> None:
    if (
        "username" not in session
        or "user_id" not in session
        or "show_hidden" not in session
        or "csrf_token" not in session
    ):
        abort(Response("You need to be logged in to perform this action", 403))


def check_csrf(csrf_token: str) -> None:
    if session["csrf_token"] != csrf_token:
        abort(403)


def check_register(username: str, password1: str, password2: str) -> list:
    errors = []

    if len(username) == 0:
        errors.append("Username can't be empty")
    elif len(username) > 64:
        errors.append("Username too long (max 64 characters)")
    if user_repository.username_taken(username):
        errors.append("Username taken")

    allowed_characters = string.ascii_letters + string.digits + string.punctuation
    if not all(character in allowed_characters for character in username):
        errors.append("Username may not contain whitespaces or non-ascii characters")

    if len(password1) == 0:
        errors.append("Password can't be empty")
    elif len(password1) > 64 or len(password2) > 64:
        errors.append("Password too long (max 64 characters)")
    if password1 != password2:
        errors.append("Passwords do not match")

    return errors


def register(username: str, password1: str, password2: str) -> list:
    errors = check_register(username, password1, password2)
    if not errors:
        user_id = user_repository.add_user(username, password1)
        session["user_id"] = user_id
        session["username"] = username
        session["show_hidden"] = False
        session["csrf_token"] = token_hex(16)
        return []
    return errors


def login(username: str, password: str) -> bool:
    if user_repository.username_exists(username) and user_repository.check_password(
        username, password
    ):
        user_id, show_hidden = user_repository.get_user_data(username)
        session["user_id"] = user_id
        session["username"] = username
        session["show_hidden"] = show_hidden
        session["csrf_token"] = token_hex(16)
        return True
    return False
