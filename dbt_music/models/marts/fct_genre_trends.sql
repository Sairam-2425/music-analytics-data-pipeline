SELECT
    EVENT_DATE,
    GENRE,

    COUNT_IF(EVENT_TYPE = 'play') AS TOTAL_PLAYS,

    COUNT(
        DISTINCT CASE
            WHEN EVENT_TYPE = 'play'
            THEN USER_ID
        END
    ) AS UNIQUE_LISTENERS,

    SUM(
        CASE
            WHEN EVENT_TYPE = 'play'
            THEN DURATION_SECONDS
            ELSE 0
        END
    ) / 60.0 AS TOTAL_LISTENING_MINUTES

FROM {{ ref('int_user_activity') }}

GROUP BY
    EVENT_DATE,
    GENRE