CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
CREATE TABLE animes (
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
    anime_id INT REFERENCES animes NOT NULL,
    synonym TEXT NOT NULL
);
CREATE TABLE relations (
    id SERIAL PRIMARY KEY,
    anime_id INT REFERENCES animes NOT NULL,
    related_id INT REFERENCES animes NOT NULL
);
CREATE TABLE list (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users NOT NULL,
    anime_id INT REFERENCES animes NOT NULL,
    episodes INT NOT NULL DEFAULT 0,
    score INT DEFAULT NULL,
    status TEXT NOT NULL DEFAULT 'Watching',
    times_watched INT NOT NULL DEFAULT 0,
    UNIQUE (user_id, anime_id)
);