# Tietokantasovellus - AnimeList

## Project Description
The website is available in [Heroku](https://tsoha-animelist.herokuapp.com/).  
The project is a website where animes are listed and users can search animes, add them to their lists to keep track of what they are watching and what they have watched. This project takes inspiration from [MyAnimeList](https://myanimelist.net).  
Anime data is taken from [here](https://github.com/manami-project/anime-offline-database) and the AGPL-3.0 license is used because of that.

## Features
- Accounts
- Listing all animes and sorting them by their average score
- Searching animes
- Personal anime list
- Importing data from MyAnimeList

### Features that I might add if I have enough time
- Seeing related animes that are not on your list
- Statistics of watched anime
- Adding users as friends
- Watch history

## Running project
### Initializing
1. Create a `.env` file at project root and add the following lines to it:
    ```
    SECRET_KEY=<secret_key>
    PEPPER=<pepper>
    DATABASE_URL=<postgresql:///user>
    ```
    and replace with corresponding values. SECRET_KEY and PEPPER should be long random strings.
3. Start virtual environment
   ```
    $ python3 -m venv venv
    $ source venv/bin/activate
    ```
4. Install dependencies
    ```
    $ pip3 install -r requirements.txt
    ```
    If installing requirements fails, try installing alternative requirements
    ```
    $ pip3 install -r requirements-alt.txt
    ```
5. Download 'anime-offline-database-minified.json' from [here](https://github.com/manami-project/anime-offline-database) and place the file at this projects root
6. Initialize database
   ```
   $ FLASK_APP=init_db.py flask run
   ```
### Running project
```
$ source venv/bin/activate
$ flask run
```