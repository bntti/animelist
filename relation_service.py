from database import database


def get_user_related_anime(user_id: int) -> list:
    sql = "SELECT a.id, a.title, a.episodes, a.thumbnail, ROUND(AVG(l2.score), 2) " \
          "FROM relations r, list l1, animes a " \
          "LEFT JOIN list l2 ON a.id = l2.anime_id " \
          "LEFT JOIN list l3 ON a.id = l3.anime_id AND l3.user_id = :user_id " \
          "WHERE l3.id IS NULL AND a.id = r.related_id " \
          "AND l1.user_id = :user_id AND l1.anime_id = r.anime_id GROUP BY a.id"
    data = database.session.execute(sql, {"user_id": user_id}).fetchall()
    return [{
        "id": row[0],
        "title": row[1],
        "episodes": row[2],
        "thumbnail": row[3],
        "score": row[4]
    } for row in data]


def get_anime_related_anime(anime_id: int) -> list:
    sql = "SELECT a.id, a.title, a.episodes, a.thumbnail, ROUND(AVG(l.score), 2) " \
          "FROM relations r, animes a LEFT JOIN list l ON l.anime_id = a.id " \
          "WHERE a.id = r.related_id AND r.anime_id = :anime_id GROUP BY a.id"
    data = database.session.execute(sql, {"anime_id": anime_id}).fetchall()
    return [{
        "id": row[0],
        "title": row[1],
        "episodes": row[2],
        "thumbnail": row[3],
        "score": row[4]
    } for row in data]
