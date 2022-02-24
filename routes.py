from typing import Union
import urllib.parse
from markupsafe import Markup
from flask import Response, flash, render_template, request, session, redirect, abort
import user_service
import list_service
import anime_service
import relation_service
import database_service
from app import app


# Url encoder
@app.template_filter('urlencode')
def url_encode(string):
    if isinstance(string, Markup):
        string = string.unescape()
    string = string.encode('utf8')
    string = urllib.parse.quote_plus(string)
    return Markup(string)


# /
@app.route("/")
def index() -> str:
    return render_template("index.html")


# /list
@app.route("/list/<path:username>", methods=["GET"])
def list_get(username) -> Union[str, Response]:
    data = user_service.get_user_data(username)
    if not data:
        return "<h1>No user found<h1>"
    user_id, _ = user_service.get_user_data(username)
    own_profile = "user_id" in session and session["user_id"] == user_id

    tag = request.args["tag"] if "tag" in request.args else ""
    status = request.args["status"] if "status" in request.args else "All"
    list_data = list_service.get_list_data(user_id, status, tag)

    return render_template(
        "list.html",
        base_url=f"/list/{url_encode(username)}",
        username=username,
        own_profile=own_profile,
        list_data=list_data,
        status=status
    )


@app.route("/list/<path:username>", methods=["POST"])
def list_post(username) -> Union[str, Response]:
    data = user_service.get_user_data(username)
    if not data:
        return list_get(username)
    user_id, _ = user_service.get_user_data(username)

    user_service.check_user()
    user_service.check_csrf(request.form["csrf_token"])
    if "user_id" not in session or session["user_id"] != user_id:
        abort(403)

    tag = request.args["tag"] if "tag" in request.args else ""
    status = request.args["status"] if "status" in request.args else "All"
    list_data = list_service.get_list_data(user_id, status, tag)

    # Handle list data change
    for anime in list_data:
        if request.form.get(f"remove_{anime['id']}"):
            list_service.remove_from_list(user_id, anime["id"])
        else:
            list_service.handle_change(
                anime["id"],
                None,
                request.form.get(f"episodes_watched_{anime['id']}"),
                request.form.get(f"status_{anime['id']}"),
                request.form.get(f"score_{anime['id']}")
            )

    flash("List updated")
    return list_get(username)


# /tags
@app.route("/tags")
def tags() -> str:
    popular_tags = database_service.get_popular_tags()
    tag_counts = database_service.get_tag_counts()
    return render_template("tags.html", popular_tags=popular_tags, tag_counts=tag_counts)


# /topanime
@app.route("/topanime", methods=["GET"])
def topanime_get() -> str:
    list_ids = []
    if "user_id" in session:
        list_ids = list_service.get_list_ids(session["user_id"])

    tag = request.args["tag"] if "tag" in request.args else ""
    query = request.args["query"] if "query" in request.args else ""
    page = 0
    if "page" in request.args and request.args["page"].isdigit():
        page = int(request.args["page"])

    anime_count = anime_service.anime_count(query, tag)
    page = max(0, min(anime_count - 50, page))
    prev_page = max(page - 50, 0)
    next_page = min(page + 50, max(0, anime_count - 50))
    top_anime = anime_service.get_top_anime(page, query, tag)

    # Base url and current url
    base_url = "/topanime?" if not query else f"/topanime?query={query}&"
    if tag:
        base_url += f"tag={url_encode(tag)}&"
    current_url = base_url if page == 0 else f"{base_url}page={page}"

    return render_template(
        "topanime.html",
        top_anime=top_anime,
        query=query,
        tag=tag,
        list_ids=list_ids,
        current_url=current_url,
        prev_url=f"{base_url}page={prev_page}",
        next_url=f"{base_url}page={next_page}",
        show_prev=prev_page != page,
        show_next=next_page != page
    )


@app.route("/topanime", methods=["POST"])
def topanime_post() -> str:
    user_service.check_user()
    user_service.check_csrf(request.form["csrf_token"])
    list_service.add_to_list(session["user_id"], int(request.form["anime_id"]))
    flash("Anime added to list")
    return topanime_get()


# /anime/id
@app.route("/anime/<int:anime_id>", methods=["GET"])
def anime_get(anime_id) -> str:
    anime = anime_service.get_anime(anime_id)
    if not anime:
        return render_template("anime.html", anime=anime)

    user_data = {"in_list": False, "score": None}
    if "user_id" in session:
        new_data = list_service.get_user_anime_data(
            session["user_id"], anime_id
        )
        user_data = new_data if new_data else user_data

    related_anime = relation_service.get_anime_related_anime(anime_id)
    anime_tags = database_service.get_tags(anime_id)

    return render_template(
        "anime.html", anime=anime, user_data=user_data, related_anime=related_anime, tags=anime_tags
    )


@app.route("/anime/<int:anime_id>", methods=["POST"])
def anime_post(anime_id) -> str:
    user_service.check_user()
    user_service.check_csrf(request.form["csrf_token"])

    anime = anime_service.get_anime(anime_id)
    if not anime:
        return anime_get(anime_id)

    # Anime is removed from list
    if request.form["submit"] == "Remove from list":
        list_service.remove_from_list(session["user_id"], anime_id)
        flash("Anime removed from list")
        return anime_get(anime_id)

    # Anime is added to list
    if request.form["submit"] == "Add to list":
        flash("Anime added to list")
        list_service.add_to_list(session["user_id"], anime_id)

    # Handle anime user data change
    list_service.handle_change(
        anime["id"],
        request.form.get("times_watched"),
        request.form.get("episodes_watched"),
        request.form.get("status"),
        request.form.get("score")
    )

    if request.form["submit"] != "Add to list":
        flash("Updated anime data")

    return anime_get(anime_id)


# /related
@app.route("/related", methods=["GET"])
def related_get() -> Union[str, Response]:
    user_service.check_user()
    related_anime = relation_service.get_user_related_anime(session["user_id"])
    return render_template("relations.html", related_anime=related_anime)


@app.route("/related", methods=["POST"])
def related_post() -> Union[str, Response]:
    user_service.check_user()
    user_service.check_csrf(request.form["csrf_token"])
    list_service.add_to_list(session["user_id"], int(request.form["anime_id"]))
    flash("Anime added to list")
    return related_get()


# /profile
@app.route("/profile/<path:username>", methods=["GET"])
def profile_get(username) -> str:
    data = user_service.get_user_data(username)
    if not data:
        return "<h1>No user found<h1>"
    user_id, _ = user_service.get_user_data(username)
    own_profile = "user_id" in session and session["user_id"] == user_id
    counts = list_service.get_counts(user_id)
    tag_counts = list_service.get_tag_counts(user_id)
    return render_template(
        "profile.html",
        own_profile=own_profile,
        username=username,
        list_url=f"/list/{url_encode(username)}",
        counts=counts,
        tag_counts=tag_counts
    )


@app.route("/profile/<path:username>", methods=["POST"])
def profile_post(username) -> str:
    data = user_service.get_user_data(username)
    if not data:
        return profile_get(username)
    user_id, _ = user_service.get_user_data(username)

    user_service.check_user()
    user_service.check_csrf(request.form["csrf_token"])
    if "user_id" not in session or session["user_id"] != user_id:
        abort(403)

    # Import from myanimelist
    if "mal_import" in request.files:
        file = request.files["mal_import"]
        if list_service.import_from_myanimelist(file):
            flash("Data imported from MyAnimeList")
            return profile_get(username)
        abort(Response("Error parsing XML file", 415))

    # "Show hidden" setting change
    new_show_hidden = bool(request.form.get("show hidden"))
    if new_show_hidden != session["show_hidden"]:
        session["show_hidden"] = new_show_hidden
        user_service.set_show_hidden(new_show_hidden)
        flash("Settings updated")

    return profile_get(username)


# /login
@app.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    username = ""
    password = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        success = user_service.login(username, password)
        if success:
            flash("Logged in")
            return redirect("/")
        flash("Wrong username or password", "error")

    return render_template("login.html", username=username, password=password)


# /register
@app.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    username = ""
    password1 = ""
    password2 = ""
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        errors = user_service.register(username, password1, password2)
        if not errors:
            flash("Account created")
            return redirect("/")
        for error in errors:
            flash(error, "error")

    return render_template(
        "register.html",
        username=username,
        password1=password1,
        password2=password2
    )


# /logout
@app.route("/logout")
def logout() -> Response:
    user_service.logout()
    flash("Logged out")
    return redirect("/")
