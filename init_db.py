import json
import sys
from typing import Callable

from tqdm import tqdm

import anime_service
import database_service


def iterate_data(data: dict, add_data_to_db: Callable[[dict, str], None]) -> None:
    for anime_data in tqdm(data["data"]):
        # Get MyAnimeList link from anime sources
        for source in anime_data["sources"]:
            if "myanimelist.net" in source:
                add_data_to_db(anime_data, source)
                break


def add_anime_data(anime_data: dict, myanimelist_link: str) -> None:
    anime = {
        "title": anime_data["title"],
        "episodes": anime_data["episodes"],
        "link": myanimelist_link,
        "picture": anime_data["picture"],
        "thumbnail": anime_data["thumbnail"],
        "hidden": "hentai" in anime_data["tags"],
    }
    anime_id = anime_service.add_anime(anime)

    # Add synonyms
    for synonym in anime_data["synonyms"]:
        database_service.add_synonym(anime_id, synonym)

    # Add tags
    for tag in anime_data["tags"]:
        database_service.add_tag(anime_id, tag)


def add_relations(anime_data: dict, myanimelist_link: str) -> None:
    anime_id = anime_service.get_anime_id(myanimelist_link)
    for relation in anime_data["relations"]:
        if "myanimelist.net" in relation:
            related_id = anime_service.get_anime_id(relation)
            if related_id:
                database_service.add_relation(anime_id, related_id)


def import_data() -> None:
    print("Opening file 'anime-offline-database-minified.json'")
    try:
        with open(
            "anime-offline-database-minified.json", "r", encoding="utf-8"
        ) as file:
            print("Loading data form file")
            data = json.load(file)
    except FileNotFoundError:
        print("Download 'anime-offline-database-minified.json' from here:")
        print("https://github.com/manami-project/anime-offline-database/")
        sys.exit(0)

    print("Initializing tables")
    database_service.init_tables()

    print("Adding anime, tags, and synonyms to the database")
    iterate_data(data, add_anime_data)

    print("Adding anime relations data to the database")
    iterate_data(data, add_relations)

    print("Committing changes")
    database_service.commit()

    print("Done!")
    sys.exit(0)


import_data()
