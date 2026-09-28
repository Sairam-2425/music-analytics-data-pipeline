SELECT
    SONG_ID,
    SONG_NAME,
    ARTIST_ID,
    ARTIST_NAME,
    GENRE,
    DURATION_SECONDS
FROM {{ source('music_raw', 'SONGS') }}