SELECT
    ARTIST_ID,
    ARTIST_NAME,
    GENRE
FROM {{ source('music_raw', 'ARTISTS') }}