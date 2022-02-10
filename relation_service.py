from database import database


def get_related_anime(user_id: int) -> list:
    sql = "SELECT a.id, a.title, a.episodes, a.thumbnail, ROUND(AVG(l2.score), 2) " \
          "FROM relations r, list l1, list l2, animes a " \
          "LEFT JOIN list l3 ON a.id = l3.anime_id AND l3.user_id = :user_id " \
          "WHERE l3.id IS NULL AND a.id = r.related_id AND l2.anime_id = a.id " \
          "AND l1.user_id = :user_id AND l1.anime_id = r.anime_id GROUP BY a.id"
    data = database.session.execute(sql, {"user_id": user_id}).fetchall()
    return [{
        "id": row[0],
        "title": row[1],
        "episodes": row[2],
        "thumbnail": row[3],
        "score": row[4]
    } for row in data]
