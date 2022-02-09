from os import getenv
from typing import Union
from flask import Flask, Response
from flask import render_template, request, session, redirect
from defusedxml.ElementTree import fromstring
from defusedxml.ElementTree import ParseError
from database import DB
import functions

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['MAX_CONTENT_LENGTH'] = 1024 ** 2
database = DB(app)


# /
@app.route("/")
def index() -> str:
    return render_template("index.html")


# /list
@app.route("/list", methods=["GET"])
def list_get() -> Union[str, Response]:
    if "user_id" not in session:
        return redirect("/login")

    user_list = database.get_list(session["user_id"])
    return render_template("list.html", user_list=user_list)


@app.route("/list", methods=["POST"])
def list_post() -> Union[str, Response]:
    if "user_id" not in session:
        return redirect("/login")

    list_animes = database.get_list(session["user_id"])

    # Import from myanimelist
    if "mal_import" in request.files:
        file = request.files["mal_import"]
        try:
            root = fromstring(file.read())
        except ParseError:
            return "<h1>Error parsing xml file</h1>", 415

        for anime_data in root:
            if anime_data.tag == "anime":
                anime = {
                    "id": anime_data.find("./series_animedb_id").text,
                    "episodes": int(anime_data.find("./my_watched_episodes").text),
                    "score": anime_data.find("./my_score").text,
                    "status": anime_data.find("./my_status").text,
                    "times_watched": int(anime_data.find("./my_times_watched").text)
                }
                if anime["status"] == "Completed":
                    anime["times_watched"] += 1
                database.import_to_list(session["user_id"], anime)

        return list_get()

    for anime in list_animes:
        if f"remove_{anime['id']}" in request.form:
            if request.form.get(f"remove_{anime['id']}"):
                database.remove_from_list(session["user_id"], anime["id"])
                continue
        if f"rate_{anime['id']}" in request.form:
            new_score = request.form.get(f"rate_{anime['id']}")
            new_score = None if new_score == "None" else int(new_score)
            if new_score != anime["score"]:
                database.set_score(session["user_id"], anime["id"], new_score)

    return list_get()


# /animes
@app.route("/animes", methods=["GET"])
def animes_get() -> str:
    if "user_id" in session:
        list_ids = database.get_list_ids(session["user_id"])
    else:
        list_ids = []

    query = request.args["query"] if "query" in request.args else ""
    page = 0
    if "page" in request.args and request.args["page"].isdigit():
        page = int(request.args["page"])

    anime_count = database.anime_count(query)
    page = max(0, min(anime_count - 50, page))
    prev_page = max(page - 50, 0)
    next_page = min(page + 50, max(0, anime_count - 50))
    animes = database.get_animes(page, query)

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
    # Anime is added to list
    if "user_id" in session:
        database.add_to_list(session["user_id"], int(request.form["anime_id"]))
    return animes_get()


# /anime/id
@app.route("/anime/<int:anime_id>", methods=["GET"])
def anime_get(anime_id) -> str:
    # Check if anime id is valid
    anime = database.get_anime(anime_id)
    if not anime:
        return render_template("anime.html", anime=anime)

    user_data = {"in_list": False, "score": None}
    if "user_id" in session:
        new_data = database.get_user_anime_data(session["user_id"], anime_id)
        user_data = new_data if new_data else user_data  # new_data can be None

    return render_template("anime.html", anime=anime, user_data=user_data)


@app.route("/anime/<int:anime_id>", methods=["POST"])
def anime_post(anime_id) -> str:
    # Check if anime id is valid and that user is logged in
    anime = database.get_anime(anime_id)
    if not anime or "user_id" not in session:
        return anime_get(anime_id)

    # Get user data
    user_data = database.get_user_anime_data(session["user_id"], anime_id)
    if user_data is None:
        user_data = {"in_list": False, "score": None}

    # Anime is removed from list
    if request.form["submit"] == "Remove from list":
        database.remove_from_list(session["user_id"], anime_id)
        return anime_get(anime_id)

    # Anime is added to list
    if request.form["submit"] == "Add to list":
        database.add_to_list(session["user_id"], anime_id)
        user_data = database.get_user_anime_data(session["user_id"], anime_id)

    # Times watched is changed
    if "times_watched" in request.form:
        new_watched = int(request.form.get("times_watched"))
        if new_watched != user_data["times_watched"]:
            database.set_times_watched(
                session["user_id"], anime["id"], new_watched
            )

    # Score is changed
    new_score = request.form.get("score")
    new_score = None if new_score == "None" else int(new_score)
    if new_score != user_data["score"]:
        database.set_score(session["user_id"], anime["id"], new_score)

    return anime_get(anime_id)


# /login
@app.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    errors = []
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        errors = functions.login(database, username, password)
        if not errors:
            user_id = database.get_user_id(username)
            session["username"] = username
            session["user_id"] = user_id
            return redirect("/")
    else:
        username = ""
        password = ""

    return render_template("login.html", errors=errors, username=username, password=password)


# /register
@app.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    errors = []
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        errors = functions.register(database, username, password1, password2)
        if not errors:
            user_id = database.add_user(username, password1)
            session["username"] = username
            session["user_id"] = user_id
            return redirect("/")
    else:
        username = ""
        password1 = ""
        password2 = ""

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
