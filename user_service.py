import random
import string
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from database import database


def generate_salt(length: int) -> str:
    symbols = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(symbols) for _ in range(length))


def hash_password(password: str, salt: str) -> str:
    password += salt
    password += getenv("PEPPER")
    return generate_password_hash(password)


def check_password(password: str, salt: str, password_hash: str) -> bool:
    password += salt
    password += getenv("PEPPER")
    return check_password_hash(password_hash, password)


def check_login(username: str, password: str) -> list:
    errors = []
    if not user_exists(username):
        errors.append("Wrong username or password")
    elif not login(username, password):
        errors.append("Wrong username or password")
    return errors


def check_register(username: str, password1: str, password2: str) -> list:
    errors = []

    if len(username) == 0:
        errors.append("Username can't be empty")
    elif len(username) > 64:
        errors.append("Username too long (max 64 characters)")
    if user_exists(username):
        errors.append("Username taken")

    allowed_characters = string.ascii_letters + string.digits + string.punctuation
    for character in username:
        if character not in allowed_characters:
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


def user_exists(username: str) -> bool:
    sql = "SELECT COUNT(*) FROM users WHERE username = LOWER(:username)"
    result = database.session.execute(sql, {"username": username})
    return result.fetchone()[0] > 0


def get_user_id(username: str) -> int:
    sql = "SELECT id FROM users WHERE username = LOWER(:username)"
    result = database.session.execute(sql, {"username": username})
    return result.fetchone()[0]


def add_user(username: str, password: str) -> int:
    salt = generate_salt(16)
    password_hash = hash_password(password, salt)

    sql = "INSERT INTO users (username, salt, password) " \
          "VALUES (LOWER(:username), :salt, :password) RETURNING id"
    result = database.session.execute(
        sql, {"username": username, "salt": salt, "password": password_hash}
    )
    database.session.commit()
    return result.fetchone()[0]


def login(username: str, password: str) -> bool:
    sql = "SELECT salt, password FROM users WHERE username = LOWER(:username)"
    result = database.session.execute(sql, {"username": username})
    salt, password_hash = result.fetchall()[0]

    return check_password(password, salt, password_hash)
