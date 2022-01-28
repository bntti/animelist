import json
from flask import Flask
from database import DB

print("Opening file 'anime-offline-database-minified.json'")
try:
    with open("anime-offline-database-minified.json", "r") as file:
        print("Loading data form file")
        data = json.load(file)
except FileNotFoundError:
    print("Download 'anime-offline-database-minified.json' from here:")
    print("https://github.com/manami-project/anime-offline-database/")
    exit(0)

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
database = DB(app)

print("Adding animes to database")
for anime_data in data["data"]:
    link = ""
    for source in anime_data["sources"]:
        if "myanimelist.net" in source:
            link = source
    anime = {
        "title": anime_data["title"],
        "episodes": anime_data["episodes"],
        "link": link,
        "picture": anime_data["picture"],
        "thumbnail": anime_data["thumbnail"]
    }
    database.add_anime(anime)

print("Commiting changes")
database.commit()

print("Done!")
exit(0)
