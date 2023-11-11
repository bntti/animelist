from sqlalchemy.sql import text

from database import database


def get_tags(anime_id: int) -> list:
    sql = """
        SELECT t.tag FROM tags t, anime a
        WHERE a.id = t.anime_id AND a.id = :anime_id
        ORDER BY t.tag
    """
    result = database.session.execute(text(sql), {"anime_id": anime_id})
    return [row[0] for row in result.fetchall()]


def get_tag_counts() -> list:
    sql = """
        SELECT t.tag, COUNT(a.id)
        FROM tags t
            LEFT JOIN anime a ON a.id = t.anime_id
        GROUP BY t.tag
        ORDER BY COUNT(a.id) DESC, t.tag
    """
    return database.session.execute(text(sql)).fetchall()


def get_popular_tags() -> list:
    sql = """
        SELECT t.tag, ROUND(AVG(l.score), 2)
        FROM tags t
            LEFT JOIN list l ON l.anime_id = t.anime_id
        GROUP BY t.tag
        ORDER BY COALESCE(AVG(l.score), 0) DESC, COUNT(l.user_id) DESC, t.tag
    """
    return database.session.execute(text(sql)).fetchall()
