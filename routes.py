from typing import Union
from flask import Response, render_template, request, session, redirect
import user_service
import list_service
import anime_service
import relation_service
from app import app


# /
@app.route("/")
def index() -> str:
    return render_template("index.html")


# /list
@app.route("/list", methods=["GET"])
def list_get() -> Union[str, Response]:
    if "user_id" not in session:
        return redirect("/login")

    list_data = list_service.get_list_data(session["user_id"])
    return render_template("list.html", list_data=list_data)


@app.route("/list", methods=["POST"])
def list_post() -> Union[str, Response]:
    if "user_id" not in session:
        return redirect("/login")

    list_data = list_service.get_list_data(session["user_id"])

    # Import from myanimelist
    if "mal_import" in request.files:
        file = request.files["mal_import"]
        if list_service.import_from_myanimelist(file):
            return list_get()
        return "<h1>Error parsing xml file</h1>", 415

    for anime in list_data:
        if f"remove_{anime['id']}" in request.form:
            if request.form.get(f"remove_{anime['id']}"):
                list_service.remove_from_list(session["user_id"], anime["id"])
                continue
        if f"rate_{anime['id']}" in request.form:
            new_score = request.form.get(f"rate_{anime['id']}")
            new_score = None if new_score == "None" else int(new_score)
            if new_score != anime["score"]:
                list_service.set_score(
                    session["user_id"], anime["id"], new_score
                )

    return list_get()


# /animes
@app.route("/animes", methods=["GET"])
def animes_get() -> str:
    list_ids = []
    if "user_id" in session:
        list_ids = list_service.get_list_ids(session["user_id"])

    query = request.args["query"] if "query" in request.args else ""
    page = 0
    if "page" in request.args and request.args["page"].isdigit():
        page = int(request.args["page"])

    anime_count = anime_service.anime_count(query)
    page = max(0, min(anime_count - 50, page))
    prev_page = max(page - 50, 0)
    next_page = min(page + 50, max(0, anime_count - 50))
    animes = anime_service.get_animes(page, query)

    # Base url and current url
    base_url = "/animes?" if not query else f"/animes?query={query}&"
    current_url = base_url if page == 0 else f"{base_url}page={page}"

    return render_template(
        "animes.html",
        animes=animes,
        query=query,
        list_ids=list_ids,
        current_url=current_url,
        prev_url=f"{base_url}page={prev_page}",
        next_url=f"{base_url}page={next_page}"
    )


@app.route("/animes", methods=["POST"])
def animes_post() -> str:
    if "user_id" in session:
        list_service.add_to_list(
            session["user_id"], int(request.form["anime_id"])
        )
    return animes_get()


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

    return render_template(
        "anime.html", anime=anime, user_data=user_data, related_anime=related_anime
    )


@app.route("/anime/<int:anime_id>", methods=["POST"])
def anime_post(anime_id) -> str:
    # Check if anime id is valid and that user is logged in
    anime = anime_service.get_anime(anime_id)
    if not anime or "user_id" not in session:
        return anime_get(anime_id)

    # Get user data
    user_data = list_service.get_user_anime_data(session["user_id"], anime_id)
    user_data = user_data if user_data else {"in_list": False, "score": None}

    # Anime is removed from list
    if request.form["submit"] == "Remove from list":
        list_service.remove_from_list(session["user_id"], anime_id)
        return anime_get(anime_id)

    # Anime is added to list
    if request.form["submit"] == "Add to list":
        list_service.add_to_list(session["user_id"], anime_id)
        user_data = list_service.get_user_anime_data(
            session["user_id"], anime_id
        )

    # Times watched is changed
    if "times_watched" in request.form:
        new_watched = int(request.form.get("times_watched"))
        if new_watched != user_data["times_watched"]:
            list_service.set_times_watched(
                session["user_id"], anime["id"], new_watched
            )

    # Score is changed
    new_score = request.form.get("score")
    new_score = None if new_score == "None" else int(new_score)
    if new_score != user_data["score"]:
        list_service.set_score(session["user_id"], anime["id"], new_score)

    return anime_get(anime_id)


# /related
@app.route("/related", methods=["GET"])
def related_get() -> Union[str, Response]:
    if "user_id" not in session:
        return redirect("/login")
    related_anime = relation_service.get_user_related_anime(session["user_id"])
    return render_template("relations.html", related_anime=related_anime)


@app.route("/related", methods=["POST"])
def related_post() -> Union[str, Response]:
    if "user_id" not in session:
        return redirect("/login")
    list_service.add_to_list(session["user_id"], int(request.form["anime_id"]))
    return related_get()


# /login
@app.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    error = False
    username = ""
    password = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = not user_service.login(username, password)
        if not error:
            return redirect("/")

    return render_template("login.html", error=error, username=username, password=password)


# /register
@app.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    errors = []
    username = ""
    password1 = ""
    password2 = ""
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        errors = user_service.register(username, password1, password2)
        if not errors:
            return redirect("/")

    return render_template(
        "register.html",
        errors=errors,
        username=username,
        password1=password1,
        password2=password2
    )


# /logout
@app.route("/logout")
def logout() -> Response:
    if "username" in session:
        del session["username"]
        del session["user_id"]
    return redirect("/")
