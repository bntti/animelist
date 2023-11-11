# Tietokantasovellus - AnimeList

## Project Description

The project is a website where anime are listed and users can search anime, add them to their lists to keep track of what they are watching and what they have watched. This project takes inspiration from [MyAnimeList](https://myanimelist.net). The website doesn't use any javascript and all css styling is made by me.

Anime data is taken from [here](https://github.com/manami-project/anime-offline-database) and the AGPL-3.0 license is used because of that

## Features

- `/`
  - Links to various parts of the website
- `/topanime`
  - Listing all anime and sorting them by their average score
  - Searching anime by name or/and by tag
  - Seeing related anime that are not on your list
- `/tags`
  - Listing tags by popularity and by count that can be used to search with in `/topanime`
- `/anime/<id>`
  - Viewing more detailed information about a specific anime
  - Editing more specific user data about anime
- `/login`, `/register`, and `/logout`
  - Accounts
- `/list/<username>`
  - Personal anime list
  - Seeing others' lists
- `/profile/<username>`
  - Importing data from MyAnimeList
  - Setting to show hidden anime (There are no hidden anime in Heroku because of database table size restrictions)
  - Statistics of watched anime
  - Seeing others' profiles

## Running project

### Dependencies

- poetry

### Initializing

1. Create a `.env` file at project root and add the following lines to it:
   ```
   SECRET_KEY=<secret_key>
   DATABASE_URL=<postgresql:///user>
   ```
   and replace with corresponding values. SECRET_KEY should be a long random string
2. Install dependencies
   ```
   poetry install
   ```
3. Download 'anime-offline-database-minified.json' from [here](https://github.com/manami-project/anime-offline-database) and place the file at this project's root
4. Initialize the database
   ```
   poetry run invoke initialize-database
   ```

### Running project

```
poetry run invoke dev
```

Or alternatively

```
poetry run invoke start
```
