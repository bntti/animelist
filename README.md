# Tietokantasovellus - AnimeList

## Project Description
Project will be a website where animes are listed and you can search animes and add them to your own list to keep track of what you are watching and what you have watched. This project takes inspiration from [MyAnimeList](https://myanimelist.net).  
Anime data is taken from [here](https://github.com/manami-project/anime-offline-database) and the AGPL-3.0 license is used because of that.

## Features
- Accounts
- Listing all animes and sorting them
- Searching animes
- Anime user ratings
- Adding animes to personal anime list and rating them
- Editing personal anime list

### Will be added if I have enough time
- Importing data from MyAnimeList
- Seeing related animes that are not in your list
- Statistics of watched anime
- Friends
- History

## Datase Tables
### Animes
| Field            | Type                                              |
| ---------------- | ------------------------------------------------- |
| ID               | `ID`                                              |
| Myanimelist link | `URL`                                             |
| title            | `String`                                          |
| type             | `Enum of [TV, MOVIE, OVA, ONA, SPECIAL, UNKNOWN]` |
| episodes         | `Integer`                                         |
| status           | `Enum of [FINISHED, ONGOING, UPCOMING, UNKNOWN]`  |
| animeSeason      | `String`                                          |
| picture          | `URL`                                             |

### Synonyms
| Field   | Type     |
| ------- | -------- |
| ID      | `ID`     |
| animeID | `ID`     |
| synonym | `String` |

### Relations
| Field    | Type |
| -------- | ---- |
| ID       | `ID` |
| animeID  | `ID` |
| relation | `ID` |

### Tags
| Field   | Type     |
| ------- | -------- |
| ID      | `ID`     |
| animeID | `ID`     |
| tag     | `String` |

### Users
| Field    | Type     |
| -------- | -------- |
| ID       | `ID`     |
| username | `String` |
| salt     | `String` |
| password | `String` |

### ListEntries
| Field     | Type                                                          |
| --------- | ------------------------------------------------------------- |
| ID        | `ID`                                                          |
| userID    | `ID`                                                          |
| animeID   | `ID`                                                          |
| rating    | `Integer`                                                     |
| status    | `Enum of [COMPLETED, WATCHING, ONHOLD, DROPPED, PLANTOWATCH]` |
| episodes  | `Integer`                                                     |
| favourite | `Boolean`                                                     |