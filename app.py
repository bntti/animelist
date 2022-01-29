from typing import Union
from os import getenv
from flask import Flask, Response
from flask import render_template, request, session, redirect
from database import DB
import functions

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
database = DB(app)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/list")
def list() -> str:
    list = database.get_list(session["user"]["id"])
    return render_template("list.html", list=list)


@app.route("/animes", methods=["GET", "POST"])
def animes() -> str:
    list = database.get_list_ids(session["user"]["id"])
    if request.method == "POST":
        if session["user"]:
            database.add_to_list(
                session["user"]["id"], request.form["anime_id"]
            )
        list = database.get_list_ids(session["user"]["id"])
    page = 0
    query = request.args["query"] if "query" in request.args else ""
    if "page" in request.args and request.args["page"].isdigit():
        page = int(request.args["page"])

    anime_count = database.anime_count(query)
    animes = database.get_animes(page, query)

    page = max(0, min(anime_count - 50, page))
    prev_page = max(page - 50, 0)
    next_page = min(page + 50, max(0, anime_count - 50))
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


@app.route("/anime/<int:id>")
def anime(id) -> str:
    anime = database.get_anime(id)
    return render_template("anime.html", anime=anime)


@app.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = functions.login(database, username, password)
        if error == "OK":
            id = database.get_user_id(username)
            session["user"] = {"username": request.form["username"], "id": id}
            return redirect("/")

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
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
    return render_template("register.html", error=error)


@app.route("/logout")
def logout() -> Response:
    if "user" in session:
        del session["user"]
    return redirect("/")
