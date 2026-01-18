CREATE TABLE IF NOT EXISTS users (
    user_id     SERIAL PRIMARY KEY,
    username    VARCHAR(50) UNIQUE NOT NULL,
    password    VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS artists (
    artist_id   SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    user_id     INT REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS albums (
    album_id    SERIAL PRIMARY KEY,
    title       VARCHAR(100) NOT NULL,
    artist_id   INT REFERENCES artists(artist_id),
    user_id     INT REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS songs (
    song_id       SERIAL PRIMARY KEY,
    title         VARCHAR(100) NOT NULL,
    artist_id     INT REFERENCES artists(artist_id),
    album_id      INT REFERENCES albums(album_id),
    duration      INT,
    file_url      VARCHAR(255),
    file_data     BYTEA,
    file_mime     VARCHAR(100),
    user_id       INT REFERENCES users(user_id),
    upload_time   TIMESTAMP
);

CREATE TABLE IF NOT EXISTS playlists (
    playlist_id SERIAL PRIMARY KEY,
    name        VARCHAR(100),
    user_id     INT REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS playlist_songs (
    playlist_id INT REFERENCES playlists(playlist_id),
    song_id     INT REFERENCES songs(song_id),
    PRIMARY KEY (playlist_id, song_id)
);
