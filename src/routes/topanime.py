from flask import Blueprint, flash, render_template, request, session

from repositories import anime_repository, list_repository, relation_repository
from routes.template_filter import url_encode
from services import user_service

topanime_bp = Blueprint("topanime", __name__)


@topanime_bp.route("/topanime", methods=["GET"])
def topanime_get() -> str:
    list_ids = []
    if "user_id" in session:
        list_ids = list_repository.get_list_ids(session["user_id"])

    related = request.args["related"] if "related" in request.args else ""
    tag = request.args["tag"].lower() if "tag" in request.args else ""
    query = request.args["query"] if "query" in request.args else ""
    page = 0
    if "page" in request.args and request.args["page"].isdigit():
        page = int(request.args["page"])

    if not related:
        anime_count = anime_repository.anime_count(query, tag)
        top_anime = anime_repository.get_top_anime(page, query, tag)
    else:
        user_service.check_user()
        anime_count = relation_repository.related_anime_count(session["user_id"])
        top_anime = relation_repository.get_related_anime(page, session["user_id"])
        tag = ""
        query = ""
    page = max(0, min(anime_count - 50, page))
    prev_page = max(page - 50, 0)
    next_page = min(page + 50, max(0, anime_count - 50))

    # Base url and current url
    base_url = "/topanime?" if not query else f"/topanime?query={query}&"
    if tag:
        base_url += f"tag={url_encode(tag)}&"
    if related:
        base_url += "related=on&"
    current_url = base_url if page == 0 else f"{base_url}page={page}"

    return render_template(
        "topanime.html",
        top_anime=top_anime,
        query=query,
        tag=tag,
        related=related,
        list_ids=list_ids,
        current_url=current_url,
        prev_url=f"{base_url}page={prev_page}",
        next_url=f"{base_url}page={next_page}",
        show_prev=prev_page != page,
        show_next=next_page != page,
    )


@topanime_bp.route("/topanime", methods=["POST"])
def topanime_post() -> str:
    user_service.check_user()
    user_service.check_csrf(request.form["csrf_token"])
    list_repository.add_to_list(session["user_id"], int(request.form["anime_id"]))
    flash("Anime added to list")
    return topanime_get()
