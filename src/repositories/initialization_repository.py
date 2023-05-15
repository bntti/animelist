from sqlalchemy.sql import text

from database import database


def init_tables() -> None:
    sql = "DROP TABLE IF EXISTS users, anime, relations, synonyms, list, tags"
    database.session.execute(text(sql))
    with open("../schema.sql", "r", encoding="utf-8") as file:
        sql = "".join(file.readlines())
    database.session.execute(text(sql))


def add_anime(anime: dict) -> int:
    sql = """
        INSERT INTO anime (title, episodes, link, picture, thumbnail, hidden)
        VALUES (:title, :episodes, :link, :picture, :thumbnail, :hidden)
        Returning id
    """
    return database.session.execute(text(sql), anime).fetchone()[0]


def add_synonym(anime_id: int, synonym: str) -> None:
    sql = "INSERT INTO synonyms (anime_id, synonym) VALUES (:anime_id, :synonym)"
    database.session.execute(text(sql), {"anime_id": anime_id, "synonym": synonym})


def add_tag(anime_id: int, tag: str) -> None:
    sql = "INSERT INTO tags (anime_id, tag) VALUES (:anime_id, :tag)"
    database.session.execute(text(sql), {"anime_id": anime_id, "tag": tag})


def add_relation(anime_id: int, related_id: int) -> None:
    sql = "INSERT INTO relations (anime_id, related_id) VALUES (:anime_id, :related_id)"
    database.session.execute(
        text(sql), {"anime_id": anime_id, "related_id": related_id}
    )


def commit() -> None:
    database.session.commit()
