from os import getenv
from flask import Flask, Response
from flask import render_template, request, session, redirect
from defusedxml.ElementTree import fromstring
from database import DB
import functions

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['MAX_CONTENT_LENGTH'] = 1024**2
database = DB(app)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/list", methods=["GET", "POST"])
def list() -> str:
    if "user_id" not in session:
        return redirect("/login")

    list = database.get_list(session["user_id"])
    if request.method == "POST":
        if "mal_import" in request.files:
            file = request.files["mal_import"]
            try:
                root = fromstring(file.read())
            except:
                return "<h1>Error parsing xml file</h1>", 415

            for anime_data in root:
                if anime_data.tag == "anime":
                    anime = {
                        "id": anime_data.find("./series_animedb_id").text,
                        "episodes": int(anime_data.find("./my_watched_episodes").text),
                        "rating": anime_data.find("./my_score").text,
                        "status": anime_data.find("./my_status").text,
                        "times_watched": int(anime_data.find("./my_times_watched").text)
                    }
                    if anime["status"] == "Completed":
                        anime["times_watched"] += 1
                    database.import_to_list(session["user_id"], anime)

        change = False
        for anime in list:
            if f"remove_{anime['id']}" in request.form:
                if request.form.get(f"remove_{anime['id']}"):
                    change = True
                    database.remove_from_list(session["user_id"], anime["id"])
                    continue
            if str(anime["id"]) in request.form:
                new_rating = request.form.get(str(anime["id"]))
                new_rating = None if new_rating == "None" else int(new_rating)
                if new_rating != anime["rating"]:
                    change = True
                    database.set_score(
                        session["user_id"], anime["id"], new_rating
                    )

            if change:
                list = database.get_list(session["user_id"])

    return render_template("list.html", list=list)


@app.route("/animes", methods=["GET", "POST"])
def animes() -> str:
    if "user_id" in session:
        list = database.get_list_ids(session["user_id"])
    else:
        list = []

    # Anime is added to list
    if request.method == "POST":
        if "user_id" in session:
            database.add_to_list(
                session["user_id"], int(request.form["anime_id"])
            )
            list.append(int(request.form["anime_id"]))

    # Current page
    page = 0
    query = request.args["query"] if "query" in request.args else ""
    if "page" in request.args and request.args["page"].isdigit():
        page = int(request.args["page"])

    anime_count = database.anime_count(query)
    page = max(0, min(anime_count - 50, page))
    prev_page = max(page - 50, 0)
    next_page = min(page + 50, max(0, anime_count - 50))
    animes = database.get_animes(page, query)

    # Base url and current url
    base_url = "/animes?"
    if query:
        base_url += f"query={query}&"
    current_url = base_url
    if page > 0:
        current_url += f"page={page}"

    return render_template(
        "animes.html",
        animes=animes,
        query=query,
        list=list,
        current_url=current_url,
        prev_url=f"{base_url}page={prev_page}",
        next_url=f"{base_url}page={next_page}"
    )


@app.route("/anime/<int:anime_id>", methods=["GET", "POST"])
def anime(anime_id) -> str:
    # Check if anime id is valid
    anime = database.get_anime(anime_id)
    if not anime:
        return render_template("anime.html", anime=anime)

    if "user_id" in session:
        user_data = database.get_user_anime_data(session["user_id"], anime_id)
        if user_data is None:
            user_data = {"in_list": False, "rating": None}
    else:
        user_data = {"in_list": False}

    # Anime is added to list or list data is edited
    if request.method == "POST":
        if "user_id" in session:
            if request.form["submit"] == "Add to list":
                # Added to list
                database.add_to_list(session["user_id"], anime_id)
                user_data = database.get_user_anime_data(
                    session["user_id"], anime_id
                )
            if request.form["submit"] == "Remove from list":
                # Removed from list
                database.remove_from_list(session["user_id"], anime_id)
                user_data = {"in_list": False, "rating": None}
                anime = database.get_anime(anime_id)
            else:
                # Times watched change
                if "times_watched" in request.form:
                    new_watched = int(request.form.get("times_watched"))
                    if new_watched != user_data["times_watched"]:
                        user_data["times_watched"] = new_watched
                        database.set_times_watched(
                            session["user_id"], anime["id"], new_watched
                        )

                # Rating change
                new_rating = request.form.get("rating")
                new_rating = None if new_rating == "None" else int(new_rating)
                if new_rating != user_data["rating"]:
                    database.set_score(
                        session["user_id"], anime["id"], new_rating
                    )
                    user_data["rating"] = new_rating
                    anime = database.get_anime(anime_id)

    return render_template("anime.html", anime=anime, user_data=user_data)


@app.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = functions.login(database, username, password)
        if error == "OK":
            user_id = database.get_user_id(username)
            session["username"] = username
            session["user_id"] = user_id
            return redirect("/")
    else:
        username = ""
        password = ""

    return render_template("login.html", error=error, username=username, password=password)


@app.route("/register", methods=["GET", "POST"])
def register() -> str | Response:
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        error = functions.register(database, username, password1, password2)
        if error == "OK":
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
        error=error,
        username=username,
        password1=password1,
        password2=password2
    )


@app.route("/logout")
def logout() -> Response:
    if "username" in session:
        del session["username"]
        del session["user_id"]
    return redirect("/")
