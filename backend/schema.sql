DROP TABLE IF EXISTS playlist_songs;
DROP TABLE IF EXISTS playlists;
DROP TABLE IF EXISTS songs;
DROP TABLE IF EXISTS albums;
DROP TABLE IF EXISTS artists;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id     SERIAL PRIMARY KEY,
    username    VARCHAR(50) UNIQUE NOT NULL,
    password    VARCHAR(100) NOT NULL
);

CREATE TABLE artists (
    artist_id   SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    user_id     INT REFERENCES users(user_id)
);

CREATE TABLE albums (
    album_id    SERIAL PRIMARY KEY,
    title       VARCHAR(100) NOT NULL,
    artist_id   INT REFERENCES artists(artist_id),
    user_id     INT REFERENCES users(user_id)
);

CREATE TABLE songs (
    song_id       SERIAL PRIMARY KEY,
    title         VARCHAR(100) NOT NULL,
    artist_id     INT REFERENCES artists(artist_id),
    album_id      INT REFERENCES albums(album_id),
    duration      INT,
    file_url      VARCHAR(255),
    user_id       INT REFERENCES users(user_id),
    upload_time   TIMESTAMP
);

CREATE TABLE playlists (
    playlist_id SERIAL PRIMARY KEY,
    name        VARCHAR(100),
    user_id     INT REFERENCES users(user_id)
);

CREATE TABLE playlist_songs (
    playlist_id INT REFERENCES playlists(playlist_id),
    song_id     INT REFERENCES songs(song_id),
    PRIMARY KEY (playlist_id, song_id)
);
