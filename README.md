# Tietokantasovellus - AnimeList

## Running project
### Initializing
1. Create a `.env` file at project root and add the following lines to it:
    ```
    SECRET_KEY=<secret_key>
    PEPPER=<pepper>
    DATABASE_URL=<postgresql:///user>
    ```
    and replace with corresponding values. SECRET_KEY and PEPPER should be long random strings.
2. Initialize database with schema.sql
   ```
   $ psql < schema.sql
   ```
3. Start virtual environment
   ```
    $ python3 -m venv venv
    $ source venv/bin/activate
    ```
4. Install dependencies
    ```
    $ pip3 install -r requirements.txt
    ```
5. Download 'anime-offline-database-minified.json' from [here](https://github.com/manami-project/anime-offline-database)
6. Import 'anime-offline-database-minified.json'
   ```
   $ FLASK_APP=import.py flask run
   ```
### Running project
```
$ source venv/bin/activate
$ flask run
```

## Project Description
The project will be a website where animes are listed and you can search animes and add them to your own list to keep track of what you are watching and what you have watched. This project takes inspiration from [MyAnimeList](https://myanimelist.net).  
Anime data is taken from [here](https://github.com/manami-project/anime-offline-database) and the AGPL-3.0 license is used because of that.

## Features
- Accounts
- Listing all animes and sorting them
- Searching animes
- Anime user ratings
- Adding animes to personal anime list and rating them
- Editing personal anime list

### Features that will be added if I have enough time
- Importing data from MyAnimeList
- Seeing related animes that are not on your list
- Statistics of watched anime
- Friends
- History
