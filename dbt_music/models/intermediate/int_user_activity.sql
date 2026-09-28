SELECT
    e.EVENT_ID,
    e.USER_ID,
    u.USER_NAME,
    u.COUNTRY,
    u.DEVICE,

    e.SONG_ID,
    s.SONG_NAME,

    e.ARTIST_ID,
    a.ARTIST_NAME,

    e.GENRE,
    e.EVENT_TYPE,
    e.DURATION_SECONDS,
    e.EVENT_TIMESTAMP,

    CAST(e.EVENT_TIMESTAMP AS DATE) AS EVENT_DATE,

    e.DURATION_SECONDS / 60.0 AS LISTENING_MINUTES

FROM {{ ref('stg_music_events') }} e

LEFT JOIN {{ ref('stg_users') }} u
    ON e.USER_ID = u.USER_ID

LEFT JOIN {{ ref('stg_songs') }} s
    ON e.SONG_ID = s.SONG_ID

LEFT JOIN {{ ref('stg_artists') }} a
    ON e.ARTIST_ID = a.ARTIST_ID