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
    if "user" not in session:
        return redirect("/login")

    list = database.get_list(session["user"]["id"])
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
                    database.import_to_list(session["user"]["id"], anime)

        change = False
        for anime in list:
            if f"remove_{anime['id']}" in request.form:
                if request.form.get(f"remove_{anime['id']}"):
                    change = True
                    database.remove_from_list(
                        session["user"]["id"], anime["id"]
                    )
                    continue
            if str(anime["id"]) in request.form:
                new_rating = request.form.get(str(anime["id"]))
                new_rating = None if new_rating == "None" else int(new_rating)
                if new_rating != anime["rating"]:
                    print(new_rating)
                    change = True
                    database.set_score(
                        session["user"]["id"], anime["id"], new_rating
                    )

            if change:
                list = database.get_list(session["user"]["id"])

    return render_template("list.html", list=list)


@app.route("/animes", methods=["GET", "POST"])
def animes() -> str:
    if "user" in session:
        list = database.get_list_ids(session["user"]["id"])
    else:
        list = []

    # Anime is added to list
    if request.method == "POST":
        if session["user"]:
            database.add_to_list(
                session["user"]["id"], int(request.form["anime_id"])
            )
        if "user" in session:
            list = database.get_list_ids(session["user"]["id"])

    # Current page
    page = 0
    query = request.args["query"] if "query" in request.args else ""
    if "page" in request.args and request.args["page"].isdigit():
        page = int(request.args["page"])

    # Anime Counts
    anime_count = database.anime_count(query)
    animes = database.get_animes(page, query)

    page = max(0, min(anime_count - 50, page))
    prev_page = max(page - 50, 0)
    next_page = min(page + 50, max(0, anime_count - 50))

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


@app.route("/anime/<int:id>", methods=["GET", "POST"])
def anime(id) -> str:
    # Check if anime id is valid
    anime = database.get_anime(id)
    if not anime:
        return render_template("anime.html", anime=anime)

    if "user" in session:
        user_data = database.get_user_anime_data(session["user"]["id"], id)
        if user_data == None:
            user_data = {"in_list": False, "rating": None}
    else:
        user_data = {"in_list": False}

    # Anime is added to list or list data is edited
    if request.method == "POST":
        if session["user"]:
            if request.form["submit"] == "Add to list":
                # Added to list
                database.add_to_list(session["user"]["id"], id)
                user_data = database.get_user_anime_data(
                    session["user"]["id"], id
                )
            if request.form["submit"] == "Remove from list":
                # Removed from list
                database.remove_from_list(session["user"]["id"], id)
                user_data = {"in_list": False, "rating": None}
                anime = database.get_anime(id)
            else:
                # Times watched change
                if "times_watched" in request.form:
                    new_watched = int(request.form.get("times_watched"))
                    if new_watched != user_data["times_watched"]:
                        user_data["times_watched"] = new_watched
                        database.set_times_watched(
                            session["user"]["id"], anime["id"], new_watched
                        )

                # Rating change
                new_rating = request.form.get("rating")
                new_rating = None if new_rating == "None" else int(new_rating)
                if new_rating != user_data["rating"]:
                    database.set_score(
                        session["user"]["id"], anime["id"], new_rating
                    )
                    user_data["rating"] = new_rating
                    anime = database.get_anime(id)

    return render_template("anime.html", anime=anime, user_data=user_data)


@app.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = functions.login(database, username, password)
        if error == "OK":
            id = database.get_user_id(username)
            session["user"] = {"username": request.form["username"], "id": id}
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
            id = database.add_user(username, password1)
            session["user"] = {"username": request.form["username"], "id": id}
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
    if "user" in session:
        del session["user"]
    return redirect("/")
