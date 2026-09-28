SELECT
    USER_ID,
    USER_NAME,
    COUNTRY,
    DEVICE
FROM {{ source('music_raw', 'USERS') }}