CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    show_hidden BOOLEAN NOT NULL DEFAULT false
);
CREATE TABLE anime (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    episodes INT NOT NULL,
    link TEXT UNIQUE NOT NULL,
    picture TEXT NOT NULL,
    thumbnail TEXT NOT NULL,
    hidden BOOLEAN NOT NULL
);
CREATE TABLE synonyms (
    id SERIAL PRIMARY KEY,
    anime_id INT REFERENCES anime NOT NULL,
    synonym TEXT NOT NULL
);
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    anime_id INT REFERENCES anime NOT NULL,
    tag TEXT NOT NULL
);
CREATE TABLE relations (
    id SERIAL PRIMARY KEY,
    anime_id INT REFERENCES anime NOT NULL,
    related_id INT REFERENCES anime NOT NULL
);
CREATE TABLE list (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users NOT NULL,
    anime_id INT REFERENCES anime NOT NULL,
    episodes INT NOT NULL DEFAULT 0,
    score INT DEFAULT NULL,
    status TEXT NOT NULL DEFAULT 'Watching',
    times_watched INT NOT NULL DEFAULT 0,
    UNIQUE (user_id, anime_id)
);