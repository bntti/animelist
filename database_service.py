from database import database


def init_tables() -> None:
    sql = "DROP TABLE IF EXISTS users, animes, relations, synonyms, list, tags"
    database.session.execute(sql)
    with open("schema.sql", "r", encoding="utf-8") as file:
        sql = ''.join(file.readlines())
    database.session.execute(sql)


def add_synonym(anime_id: int, synonym: str) -> None:
    sql = "INSERT INTO synonyms (anime_id, synonym) VALUES (:anime_id, :synonym)"
    database.session.execute(
        sql, {"anime_id": anime_id, "synonym": synonym}
    )


def add_tag(anime_id: int, tag: str) -> None:
    sql = "INSERT INTO tags (anime_id, tag) VALUES (:anime_id, :tag)"
    database.session.execute(sql, {"anime_id": anime_id, "tag": tag})


def get_tags(anime_id: int) -> list:
    sql = "SELECT t.tag FROM tags t, animes a " \
          "WHERE a.id = t.anime_id AND a.id = :anime_id ORDER BY t.tag"
    result = database.session.execute(sql, {"anime_id": anime_id})
    return [row[0] for row in result.fetchall()]


def add_relation(anime_id: int, related_id: int) -> None:
    sql = "INSERT INTO relations (anime_id, related_id) VALUES (:anime_id, :related_id)"
    database.session.execute(
        sql, {"anime_id": anime_id, "related_id": related_id}
    )


def commit() -> None:
    database.session.commit()
