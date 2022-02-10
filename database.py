from os import getenv
from flask_sqlalchemy import SQLAlchemy
from app import app

url = getenv("DATABASE_URL")
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = url
database = SQLAlchemy(app)


def init_tables() -> None:
    sql = "DROP TABLE IF EXISTS users, animes, relations, synonyms, list"
    database.session.execute(sql)
    with open("schema.sql", "r", encoding="utf-8") as file:
        sql = ''.join(file.readlines())
    database.session.execute(sql)


def add_synonym(anime_id: int, synonym: str) -> None:
    sql = "INSERT INTO synonyms (anime_id, synonym) VALUES (:anime_id, :synonym)"
    database.session.execute(
        sql, {"anime_id": anime_id, "synonym": synonym}
    )


def add_relation(anime_id: int, related_id: int) -> None:
    sql = "INSERT INTO relations (anime_id, related_id) VALUES (:anime_id, :related_id)"
    database.session.execute(
        sql, {"anime_id": anime_id, "related_id": related_id}
    )
