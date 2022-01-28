from os import getenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from password import generate_salt, hash_password, check_password


class DB:
    def __init__(self, app: Flask) -> None:
        app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
        self.database = SQLAlchemy(app)

    def commit(self) -> None:
        self.database.session.commit()

    # Users table
    def user_exists(self, username: str) -> bool:
        username = username.lower()

        sql = "SELECT COUNT(*) FROM users WHERE username = :username"
        result = self.database.session.execute(sql, {"username": username})

        return result.fetchone()[0] > 0

    def add_user(self, username: str, password: str) -> None:
        username = username.lower()
        salt = generate_salt(16)
        password_hash = hash_password(password, salt)

        sql = "INSERT INTO users (username, salt, password) " \
              "VALUES (:username, :salt, :password)"
        self.database.session.execute(
            sql, {"username": username, "salt": salt, "password": password_hash}
        )
        self.commit()

    def login(self, username: str, password: str) -> bool:
        username = username.lower()

        sql = "SELECT salt, password " \
              "FROM users WHERE username = :username"
        result = self.database.session.execute(
            sql, {"username": username}
        )
        salt, password_hash = result.fetchall()[0]

        return check_password(password, salt, password_hash)

    # Animes table
    def add_anime(self, anime: dict) -> None:
        sql = "INSERT INTO animes (title, episodes, link, picture, thumbnail) " \
              "VALUES (:title, :episodes, :link, :picture, :thumbnail)"
        self.database.session.execute(sql, anime)

    def get_anime(self, page: int) -> None:
        sql = "SELECT title, thumbnail FROM animes "\
              "ORDER BY title LIMIT 50 OFFSET :offset"
        result = self.database.session.execute(sql, {"offset": page})
        animes = []
        for row in result.fetchall():
            animes.append({
                "title": row[0],
                "thumbnail": row[1]
            })
        return animes
