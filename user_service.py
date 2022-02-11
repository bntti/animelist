import string
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from database import database


def check_password(username: str, password: str) -> bool:
    sql = "SELECT password FROM users WHERE username = LOWER(:username)"
    result = database.session.execute(sql, {"username": username})
    password_hash = result.fetchone()[0]
    return check_password_hash(password_hash, password)


def user_exists(username: str) -> bool:
    sql = "SELECT COUNT(*) FROM users WHERE username = LOWER(:username)"
    result = database.session.execute(sql, {"username": username})
    return result.fetchone()[0] > 0


def get_user_id(username: str) -> int:
    sql = "SELECT id FROM users WHERE username = LOWER(:username)"
    result = database.session.execute(sql, {"username": username})
    return result.fetchone()[0]


def add_user(username: str, password: str) -> int:
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password) VALUES (LOWER(:username), :password) RETURNING id"
    result = database.session.execute(
        sql, {"username": username, "password": password_hash}
    )
    database.session.commit()
    return result.fetchone()[0]


def check_register(username: str, password1: str, password2: str) -> list:
    errors = []

    if len(username) == 0:
        errors.append("Username can't be empty")
    elif len(username) > 64:
        errors.append("Username too long (max 64 characters)")
    if user_exists(username):
        errors.append("Username taken")

    allowed_characters = string.ascii_letters + string.digits + string.punctuation
    if not all(character in allowed_characters for character in username):
        errors.append(
            "Username may not contain whitespaces or non-ascii characters"
        )

    if len(password1) == 0:
        errors.append("Password can't be empty")
    elif len(password1) > 64 or len(password2) > 64:
        errors.append("Password too long (max 64 characters)")
    if password1 != password2:
        errors.append("Passwords do not mach")

    return errors


def register(username: str, password1: str, password2: str) -> list:
    errors = check_register(username, password1, password2)
    if not errors:
        user_id = add_user(username, password1)
        session["username"] = username
        session["user_id"] = user_id
        return []
    return errors


def login(username: str, password: str) -> bool:
    if user_exists(username) and check_password(username, password):
        user_id = get_user_id(username)
        session["username"] = username
        session["user_id"] = user_id
        return True
    return False
