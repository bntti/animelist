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

print("Adding animes and tags to database")
anime_count = len(data["data"])
for i, anime_data in enumerate(data["data"]):
    if i % (anime_count // 10) == 0:
        print(f"{100*i/anime_count:.0f}% done")

    myanimelist_link = ""
    for source in anime_data["sources"]:
        if "myanimelist.net" in source:
            myanimelist_link = source

    # Ignore some animes
    if myanimelist_link == "" or "year" not in anime_data["animeSeason"]:
        continue

    link = ""
    for source in anime_data["sources"]:
        if "myanimelist.net" in source:
            link = source
    anime = {
        "title": anime_data["title"],
        "episodes": anime_data["episodes"],
        "link": link,
        "picture": anime_data["picture"],
        "thumbnail": anime_data["thumbnail"],
        "hidden": "hentai" in anime_data["tags"]
    }
    anime_id = database.add_anime(anime)
    for tag in anime_data["tags"]:
        database.add_tag(anime_id, tag)
    for synonym in anime_data["synonyms"]:
        database.add_synonym(anime_id, synonym)

print("Commiting changes")
database.commit()

print("Done!")
exit(0)
