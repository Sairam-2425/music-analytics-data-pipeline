import streamlit as st
import pandas as pd
import snowflake.connector


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Music Analytics Dashboard",
    page_icon="🎵",
    layout="wide"
)


# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

@st.cache_resource
def get_snowflake_connection():

    connection = snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
        role=st.secrets["snowflake"]["role"]
    )

    return connection


# ============================================================
# GET DATE RANGE
# ============================================================

@st.cache_data
def get_date_range():

    query = """
        SELECT
            MIN(EVENT_DATE) AS MIN_DATE,
            MAX(EVENT_DATE) AS MAX_DATE
        FROM FCT_DAILY_ACTIVE_LISTENERS
    """

    return pd.read_sql(
        query,
        get_snowflake_connection()
    )


# ============================================================
# DAILY ACTIVE LISTENERS
# ============================================================

@st.cache_data
def get_daily_active_listeners(start_date, end_date):

    query = """
        SELECT
            EVENT_DATE,
            DAILY_ACTIVE_LISTENERS
        FROM FCT_DAILY_ACTIVE_LISTENERS
        WHERE EVENT_DATE BETWEEN %s AND %s
        ORDER BY EVENT_DATE
    """

    return pd.read_sql(
        query,
        get_snowflake_connection(),
        params=[start_date, end_date]
    )


# ============================================================
# KPI DATA
# ============================================================

@st.cache_data
def get_kpis():

    query = """
        SELECT

            (
                SELECT COALESCE(SUM(TOTAL_PLAYS), 0)
                FROM FCT_SONG_POPULARITY
            ) AS TOTAL_PLAYS,

            (
                SELECT COUNT(*)
                FROM FCT_USER_LISTENING
            ) AS TOTAL_USERS,

            (
                SELECT COUNT(*)
                FROM FCT_SONG_POPULARITY
            ) AS TOTAL_SONGS,

            (
                SELECT COUNT(*)
                FROM FCT_ARTIST_PERFORMANCE
            ) AS TOTAL_ARTISTS,

            (
                SELECT COALESCE(
                    SUM(TOTAL_LISTENING_MINUTES),
                    0
                )
                FROM FCT_SONG_POPULARITY
            ) / 60.0 AS TOTAL_LISTENING_HOURS,

            (
                SELECT COALESCE(
                    AVG(DAILY_ACTIVE_LISTENERS),
                    0
                )
                FROM FCT_DAILY_ACTIVE_LISTENERS
            ) AS AVG_DAILY_ACTIVE_LISTENERS,

            (
                SELECT COALESCE(SUM(TOTAL_LIKES), 0)
                FROM FCT_SONG_POPULARITY
            ) AS TOTAL_LIKES
    """

    return pd.read_sql(
        query,
        get_snowflake_connection()
    )


# ============================================================
# TOP SONGS
# ============================================================

@st.cache_data
def get_top_songs():

    query = """
        SELECT
            SONG_NAME,
            ARTIST_NAME,
            TOTAL_PLAYS
        FROM FCT_SONG_POPULARITY
        ORDER BY TOTAL_PLAYS DESC
        LIMIT 10
    """

    return pd.read_sql(
        query,
        get_snowflake_connection()
    )


# ============================================================
# TOP ARTISTS
# ============================================================

@st.cache_data
def get_top_artists():

    query = """
        SELECT
            ARTIST_NAME,
            TOTAL_PLAYS
        FROM FCT_ARTIST_PERFORMANCE
        ORDER BY TOTAL_PLAYS DESC
        LIMIT 10
    """

    return pd.read_sql(
        query,
        get_snowflake_connection()
    )


# ============================================================
# GENRE TRENDS
# ============================================================

@st.cache_data
def get_genre_trends():

    query = """
        SELECT
            EVENT_DATE,
            GENRE,
            TOTAL_PLAYS
        FROM FCT_GENRE_TRENDS
        ORDER BY EVENT_DATE
    """

    return pd.read_sql(
        query,
        get_snowflake_connection()
    )


# ============================================================
# FILTER OPTIONS
# ============================================================

@st.cache_data
def get_filter_options():

    query = """
        SELECT DISTINCT
            COUNTRY,
            DEVICE
        FROM FCT_USER_LISTENING
    """

    return pd.read_sql(
        query,
        get_snowflake_connection()
    )


# ============================================================
# FILTERED USERS
# ============================================================

@st.cache_data
def get_filtered_users(country, device):

    query = """
        SELECT
            USER_ID,
            USER_NAME,
            COUNTRY,
            DEVICE,
            TOTAL_PLAYS,
            TOTAL_LIKES,
            TOTAL_SKIPS,
            UNIQUE_SONGS_LISTENED,
            UNIQUE_ARTISTS_LISTENED,
            TOTAL_LISTENING_MINUTES
        FROM FCT_USER_LISTENING
        WHERE 1 = 1
    """

    params = []

    if country != "All":

        query += """
            AND COUNTRY = %s
        """

        params.append(country)

    if device != "All":

        query += """
            AND DEVICE = %s
        """

        params.append(device)

    query += """
        ORDER BY TOTAL_PLAYS DESC
        LIMIT 10
    """

    return pd.read_sql(
        query,
        get_snowflake_connection(),
        params=params
    )


# ============================================================
# COUNTRY ANALYSIS
# ============================================================

@st.cache_data
def get_country_analysis():

    query = """
        SELECT
            COUNTRY,
            COUNT(DISTINCT USER_ID) AS TOTAL_USERS,
            COALESCE(SUM(TOTAL_PLAYS), 0) AS TOTAL_PLAYS,
            COALESCE(
                SUM(TOTAL_LISTENING_MINUTES),
                0
            ) AS TOTAL_LISTENING_MINUTES
        FROM FCT_USER_LISTENING
        GROUP BY COUNTRY
        ORDER BY TOTAL_PLAYS DESC
    """

    return pd.read_sql(
        query,
        get_snowflake_connection()
    )


# ============================================================
# DEVICE ANALYSIS
# ============================================================

@st.cache_data
def get_device_analysis():

    query = """
        SELECT
            DEVICE,
            COUNT(DISTINCT USER_ID) AS TOTAL_USERS,
            COALESCE(SUM(TOTAL_PLAYS), 0) AS TOTAL_PLAYS,
            COALESCE(
                SUM(TOTAL_LISTENING_MINUTES),
                0
            ) AS TOTAL_LISTENING_MINUTES
        FROM FCT_USER_LISTENING
        GROUP BY DEVICE
        ORDER BY TOTAL_PLAYS DESC
    """

    return pd.read_sql(
        query,
        get_snowflake_connection()
    )


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.title("🎵 Music Analytics Dashboard")

st.write(
    "Analytics dashboard powered by Snowflake and dbt."
)


# ============================================================
# SNOWFLAKE CONNECTION STATUS
# ============================================================

try:

    get_snowflake_connection()

    st.success(
        "Connected to Snowflake successfully!"
    )

except Exception as e:

    st.error(
        f"Unable to connect to Snowflake: {e}"
    )

    st.stop()


# ============================================================
# DASHBOARD FILTERS
# ============================================================

st.subheader("🎛️ Dashboard Filters")

try:

    filter_df = get_filter_options()

    countries = sorted(
        filter_df["COUNTRY"]
        .dropna()
        .unique()
        .tolist()
    )

    devices = sorted(
        filter_df["DEVICE"]
        .dropna()
        .unique()
        .tolist()
    )

except Exception as e:

    st.error(
        f"Unable to load filter options: {e}"
    )

    countries = []
    devices = []


col1, col2 = st.columns(2)

with col1:

    selected_country = st.selectbox(
        "🌍 Select Country",
        ["All"] + countries
    )

with col2:

    selected_device = st.selectbox(
        "📱 Select Device",
        ["All"] + devices
    )


# ============================================================
# DATE FILTER
# ============================================================

st.subheader("📅 Date Filter")

try:

    date_df = get_date_range()

    min_date = pd.to_datetime(
        date_df["MIN_DATE"].iloc[0]
    ).date()

    max_date = pd.to_datetime(
        date_df["MAX_DATE"].iloc[0]
    ).date()

    selected_dates = st.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Make sure the user selected a complete range
    if len(selected_dates) != 2:

        st.warning(
            "Please select both a start date and an end date."
        )

        selected_start_date = min_date
        selected_end_date = max_date

    else:

        selected_start_date = selected_dates[0]
        selected_end_date = selected_dates[1]

except Exception as e:

    st.error(
        f"Unable to load date filter: {e}"
    )

    selected_start_date = None
    selected_end_date = None


# ============================================================
# KEY PERFORMANCE INDICATORS
# ============================================================

st.subheader("📊 Key Performance Indicators")

try:

    kpi_df = get_kpis()

    kpi = kpi_df.iloc[0]

    # --------------------------------------------------------
    # FIRST ROW
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            label="Total Plays",
            value=f"{int(kpi['TOTAL_PLAYS']):,}"
        )

    with col2:

        st.metric(
            label="Total Users",
            value=f"{int(kpi['TOTAL_USERS']):,}"
        )

    with col3:

        st.metric(
            label="Total Songs",
            value=f"{int(kpi['TOTAL_SONGS']):,}"
        )

    with col4:

        st.metric(
            label="Total Artists",
            value=f"{int(kpi['TOTAL_ARTISTS']):,}"
        )

    # --------------------------------------------------------
    # SECOND ROW
    # --------------------------------------------------------

    col5, col6, col7 = st.columns(3)

    with col5:

        st.metric(
            label="Listening Hours",
            value=f"{float(kpi['TOTAL_LISTENING_HOURS']):,.1f}"
        )

    with col6:

        st.metric(
            label="Avg Daily Active Listeners",
            value=f"{float(kpi['AVG_DAILY_ACTIVE_LISTENERS']):,.0f}"
        )

    with col7:

        st.metric(
            label="Total Likes",
            value=f"{int(kpi['TOTAL_LIKES']):,}"
        )

except Exception as e:

    st.error(
        f"Unable to load KPI data: {e}"
    )


# ============================================================
# DAILY ACTIVE LISTENERS
# ============================================================

st.subheader("📈 Daily Active Listeners")

try:

    if (
        selected_start_date is not None
        and selected_end_date is not None
    ):

        df_dau = get_daily_active_listeners(
            selected_start_date,
            selected_end_date
        )

        if df_dau.empty:

            st.warning(
                "No daily active listener data found "
                "for the selected date range."
            )

        else:

            df_dau["EVENT_DATE"] = pd.to_datetime(
                df_dau["EVENT_DATE"]
            )

            st.line_chart(
                df_dau.set_index("EVENT_DATE")[
                    "DAILY_ACTIVE_LISTENERS"
                ]
            )

except Exception as e:

    st.error(
        f"Unable to load daily active listeners: {e}"
    )


# ============================================================
# TOP 10 SONGS
# ============================================================

st.subheader("🎵 Top 10 Songs")

try:

    df_top_songs = get_top_songs()

    if df_top_songs.empty:

        st.warning("No song data available.")

    else:

        df_top_songs["SONG_LABEL"] = (
            df_top_songs["SONG_NAME"]
            + " - "
            + df_top_songs["ARTIST_NAME"]
        )

        st.bar_chart(
            df_top_songs.set_index("SONG_LABEL")[
                "TOTAL_PLAYS"
            ]
        )

        st.dataframe(
            df_top_songs[
                [
                    "SONG_NAME",
                    "ARTIST_NAME",
                    "TOTAL_PLAYS"
                ]
            ],
            use_container_width=True
        )

except Exception as e:

    st.error(
        f"Unable to load top songs: {e}"
    )


# ============================================================
# TOP 10 ARTISTS
# ============================================================

st.subheader("🎤 Top 10 Artists")

try:

    df_top_artists = get_top_artists()

    if df_top_artists.empty:

        st.warning("No artist data available.")

    else:

        st.bar_chart(
            df_top_artists.set_index("ARTIST_NAME")[
                "TOTAL_PLAYS"
            ]
        )

        st.dataframe(
            df_top_artists,
            use_container_width=True
        )

except Exception as e:

    st.error(
        f"Unable to load top artists: {e}"
    )


# ============================================================
# GENRE TRENDS
# ============================================================

st.subheader("🎶 Genre Trends")

try:

    df_genre = get_genre_trends()

    if df_genre.empty:

        st.warning("No genre trend data available.")

    else:

        df_genre["EVENT_DATE"] = pd.to_datetime(
            df_genre["EVENT_DATE"]
        )

        genre_chart = df_genre.pivot_table(
            index="EVENT_DATE",
            columns="GENRE",
            values="TOTAL_PLAYS",
            aggfunc="sum"
        )

        st.line_chart(
            genre_chart
        )

except Exception as e:

    st.error(
        f"Unable to load genre trends: {e}"
    )


# ============================================================
# TOP 10 USERS
# ============================================================

st.subheader("👤 Top 10 Users by Plays")

try:

    df_users = get_filtered_users(
        selected_country,
        selected_device
    )

    if df_users.empty:

        st.warning(
            "No users found for the selected filters."
        )

    else:

        st.bar_chart(
            df_users.set_index("USER_NAME")[
                "TOTAL_PLAYS"
            ]
        )

        st.dataframe(
            df_users[
                [
                    "USER_NAME",
                    "COUNTRY",
                    "DEVICE",
                    "TOTAL_PLAYS",
                    "TOTAL_LIKES",
                    "TOTAL_SKIPS",
                    "UNIQUE_SONGS_LISTENED",
                    "UNIQUE_ARTISTS_LISTENED",
                    "TOTAL_LISTENING_MINUTES"
                ]
            ],
            use_container_width=True
        )

except Exception as e:

    st.error(
        f"Unable to load user listening data: {e}"
    )


# ============================================================
# COUNTRY AND DEVICE ANALYSIS
# ============================================================

st.subheader("🌍 Geographic & Device Analysis")

col1, col2 = st.columns(2)


# ============================================================
# COUNTRY ANALYSIS
# ============================================================

with col1:

    st.markdown("### 🌍 Listening by Country")

    try:

        df_country = get_country_analysis()

        if df_country.empty:

            st.warning(
                "No country data available."
            )

        else:

            st.bar_chart(
                df_country.set_index("COUNTRY")[
                    "TOTAL_PLAYS"
                ]
            )

            st.dataframe(
                df_country,
                use_container_width=True
            )

    except Exception as e:

        st.error(
            f"Unable to load country data: {e}"
        )


# ============================================================
# DEVICE ANALYSIS
# ============================================================

with col2:

    st.markdown("### 📱 Listening by Device")

    try:

        df_device = get_device_analysis()

        if df_device.empty:

            st.warning(
                "No device data available."
            )

        else:

            st.bar_chart(
                df_device.set_index("DEVICE")[
                    "TOTAL_PLAYS"
                ]
            )

            st.dataframe(
                df_device,
                use_container_width=True
            )

    except Exception as e:

        st.error(
            f"Unable to load device data: {e}"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🎵 Music Analytics Dashboard | "
    "Powered by Streamlit, Snowflake & dbt"
)
