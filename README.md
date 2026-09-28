# 🎵 Music Analytics Data Pipeline

An end-to-end **Music Analytics Data Engineering project** that generates simulated music listening events, ingests them into **Snowflake**, transforms and tests the data using **dbt**, and presents business insights through an interactive **Streamlit dashboard**.

The project demonstrates a modern data engineering workflow from raw data ingestion to analytics and visualization.

---

## 📌 Project Overview

Music platforms generate large amounts of user activity data such as:

* User listening activity
* Song plays
* Likes
* Skips
* Artist performance
* Genre trends
* Listening duration
* Daily active listeners
* User behavior
* Country and device usage

This project builds a complete analytics pipeline to transform raw music event data into business-ready datasets and dashboards.

---

## 🏗️ Architecture

```text
                    Python Data Generator
                            │
                            ▼
                       CSV Files
                            │
                            ▼
                Snowflake Internal Stage
                            │
                            ▼
                     Snowflake RAW
                            │
                            ▼
                     dbt STAGING
                            │
                            ▼
                  dbt INTERMEDIATE
                            │
                            ▼
                     dbt MARTS
                            │
                            ▼
                   Snowflake Analytics
                            │
                            ▼
                   Streamlit Dashboard
```

### Data Flow

```text
Python
  ↓
Generate Users / Artists / Songs / Events
  ↓
CSV Files
  ↓
Snowflake Internal Stage
  ↓
RAW Tables
  ↓
dbt Staging Models
  ↓
Data Quality Tests
  ↓
Intermediate Model
  ↓
Analytics Marts
  ↓
Streamlit Dashboard
```

---

## 🛠️ Technologies Used

| Technology               | Purpose                           |
| ------------------------ | --------------------------------- |
| Python                   | Generate simulated music data     |
| CSV                      | Source data format                |
| Snowflake                | Cloud data warehouse              |
| Snowflake Internal Stage | File ingestion                    |
| Snowflake `COPY INTO`    | Load CSV data into RAW tables     |
| dbt                      | Data transformation and testing   |
| SQL                      | Data transformation and analytics |
| Streamlit                | Interactive dashboard             |
| Pandas                   | Data handling in Streamlit        |
| Git/GitHub               | Version control                   |

---

# 📂 Project Structure

```text
music-analytics-data-pipeline/
│
├── producer/
│   └── generate_music_data.py
│
├── data/
│   ├── users.csv
│   ├── artists.csv
│   ├── songs.csv
│   └── music_events.csv
│
├── dbt_music/
│   ├── dbt_project.yml
│   │
│   └── models/
│       ├── staging/
│       │   ├── sources.yml
│       │   ├── schema.yml
│       │   ├── stg_users.sql
│       │   ├── stg_artists.sql
│       │   ├── stg_songs.sql
│       │   └── stg_music_events.sql
│       │
│       ├── intermediate/
│       │   └── int_user_activity.sql
│       │
│       └── marts/
│           ├── schema.yml
│           ├── fct_song_popularity.sql
│           ├── fct_artist_performance.sql
│           ├── fct_genre_trends.sql
│           ├── fct_user_listening.sql
│           └── fct_daily_active_listeners.sql
│
├── streamlit_app/
│   ├── app.py
│   └── .streamlit/
│       └── secrets.toml.example
│
├── .gitignore
└── README.md
```

> `profiles.yml` and `secrets.toml` are intentionally excluded from GitHub because they contain credentials.

---

# 1️⃣ Data Generation

The project starts with a Python data generator.

File:

```text
producer/generate_music_data.py
```

The generator creates four datasets:

### Users

Contains information such as:

```text
USER_ID
USER_NAME
COUNTRY
DEVICE
```

### Artists

```text
ARTIST_ID
ARTIST_NAME
GENRE
```

### Songs

```text
SONG_ID
SONG_NAME
ARTIST_ID
ARTIST_NAME
GENRE
DURATION_SECONDS
```

### Music Events

```text
EVENT_ID
USER_ID
SONG_ID
SONG_NAME
ARTIST_ID
ARTIST_NAME
GENRE
EVENT_TYPE
DURATION_SECONDS
DEVICE
COUNTRY
EVENT_TIMESTAMP
```

Supported event types:

```text
play
pause
skip
like
```

The generated data is synthetic and is intended for learning and demonstration purposes.

---

# 2️⃣ Snowflake Ingestion Layer

The generated CSV files are loaded into Snowflake.

The pipeline uses a Snowflake **Internal Stage** as the ingestion point.

```text
CSV
 ↓
Snowflake Internal Stage
 ↓
COPY INTO
 ↓
RAW Tables
```

---

## Snowflake Database

```sql
CREATE DATABASE IF NOT EXISTS MUSIC_ANALYTICS;

USE DATABASE MUSIC_ANALYTICS;
```

Schemas:

```text
RAW
STAGING
ANALYTICS
```

The RAW layer stores the source data with minimal transformation.

---

## RAW Tables

The project uses four RAW tables:

```text
RAW.USERS
RAW.ARTISTS
RAW.SONGS
RAW.MUSIC_EVENTS
```

---

## File Format

CSV files are loaded using a Snowflake CSV file format.

```sql
CREATE OR REPLACE FILE FORMAT RAW.MUSIC_CSV_FORMAT
    TYPE = 'CSV'
    SKIP_HEADER = 1
    FIELD_DELIMITER = ','
    FIELD_OPTIONALLY_ENCLOSED_BY = '"';
```

---

## Internal Stage

```sql
CREATE OR REPLACE STAGE RAW.MUSIC_STAGE
    FILE_FORMAT = RAW.MUSIC_CSV_FORMAT;
```

Files are uploaded using Snowflake's `PUT` command and then loaded into RAW tables using `COPY INTO`.

Example:

```sql
PUT 'file://C:\path\to\data\users.csv'
    @RAW.MUSIC_STAGE
    AUTO_COMPRESS=TRUE;
```

Then:

```sql
COPY INTO RAW.USERS
FROM @RAW.MUSIC_STAGE
FILES = ('users.csv.gz')
FILE_FORMAT = (FORMAT_NAME = RAW.MUSIC_CSV_FORMAT);
```

The same approach is used for artists, songs and music events.

---

# 3️⃣ Data Validation in Snowflake

After ingestion, the data is validated.

Example:

```sql
SELECT COUNT(*) FROM RAW.USERS;

SELECT COUNT(*) FROM RAW.ARTISTS;

SELECT COUNT(*) FROM RAW.SONGS;

SELECT COUNT(*) FROM RAW.MUSIC_EVENTS;
```

Sample records can be inspected using:

```sql
SELECT * FROM RAW.USERS LIMIT 5;

SELECT * FROM RAW.MUSIC_EVENTS LIMIT 5;
```

Relationships between datasets can also be checked.

For example:

```sql
SELECT
    e.EVENT_ID,
    e.USER_ID,
    u.USER_NAME,
    e.SONG_ID,
    e.SONG_NAME,
    e.ARTIST_NAME,
    e.GENRE,
    e.EVENT_TYPE
FROM RAW.MUSIC_EVENTS e
JOIN RAW.USERS u
    ON e.USER_ID = u.USER_ID
LIMIT 10;
```

---

# 4️⃣ dbt Transformation Layer

dbt is used to transform the RAW data into analytics-ready datasets.

The dbt project is:

```text
dbt_music/
```

The transformation architecture contains three layers:

```text
RAW
 ↓
STAGING
 ↓
INTERMEDIATE
 ↓
MARTS
```

---

# 5️⃣ dbt STAGING Layer

The staging layer creates clean models from the RAW tables.

Models:

```text
stg_users
stg_artists
stg_songs
stg_music_events
```

Example:

```sql
SELECT
    USER_ID,
    USER_NAME,
    COUNTRY,
    DEVICE
FROM {{ source('music_raw', 'USERS') }}
```

The staging layer provides a clean and consistent starting point for downstream transformations.

---

# 6️⃣ dbt Data Quality Tests

Data quality tests are defined in:

```text
models/staging/schema.yml
```

The project uses tests such as:

* `not_null`
* `unique`
* `relationships`
* `accepted_values`

For example, `USER_ID` must be unique and not null.

Music event relationships are also tested.

For example:

```text
MUSIC_EVENTS.USER_ID
        ↓
USERS.USER_ID
```

and:

```text
MUSIC_EVENTS.SONG_ID
        ↓
SONGS.SONG_ID
```

The event type is restricted to:

```text
play
pause
skip
like
```

Run tests using:

```bash
dbt test
```

---

# 7️⃣ dbt INTERMEDIATE Layer

The intermediate model combines the staging datasets.

Model:

```text
int_user_activity.sql
```

It joins:

```text
Users
Songs
Artists
Music Events
```

The model also derives:

```text
EVENT_DATE
LISTENING_MINUTES
```

Example:

```sql
CAST(e.EVENT_TIMESTAMP AS DATE) AS EVENT_DATE
```

and:

```sql
e.DURATION_SECONDS / 60.0 AS LISTENING_MINUTES
```

This creates a reusable analytical dataset for the marts.

---

# 8️⃣ dbt MARTS Layer

The marts layer contains business-ready datasets.

### Song Popularity

```text
fct_song_popularity
```

Provides:

* Total plays
* Total likes
* Total skips
* Unique listeners
* Listening minutes

---

### Artist Performance

```text
fct_artist_performance
```

Provides:

* Total plays
* Total likes
* Total skips
* Unique listeners
* Listening minutes

---

### Genre Trends

```text
fct_genre_trends
```

Provides daily genre-level listening activity.

Metrics include:

* Total plays
* Unique listeners
* Listening minutes

---

### User Listening

```text
fct_user_listening
```

Provides:

* Total plays
* Total likes
* Total skips
* Unique songs listened
* Unique artists listened
* Total listening minutes

---

### Daily Active Listeners

```text
fct_daily_active_listeners
```

Provides:

```text
EVENT_DATE
DAILY_ACTIVE_LISTENERS
```

A daily active listener is defined in this project as a unique user who generated at least one `play` event on that date.

---

# 9️⃣ dbt Commands

Install the Snowflake adapter:

```bash
pip install dbt-snowflake
```

Check the installation:

```bash
dbt --version
```

Validate the dbt connection:

```bash
dbt debug
```

Run staging:

```bash
dbt run --select staging
```

Run the intermediate model:

```bash
dbt run --select int_user_activity
```

Run marts:

```bash
dbt run --select marts
```

Run tests:

```bash
dbt test
```

Build the complete project:

```bash
dbt build
```

Generate documentation:

```bash
dbt docs generate
```

Run documentation locally:

```bash
dbt docs serve
```

---

# 🔟 Streamlit Dashboard

The final analytics layer is an interactive Streamlit dashboard.

Application:

```text
streamlit_app/app.py
```

Run the dashboard:

```bash
streamlit run app.py
```

The dashboard connects directly to Snowflake and queries the dbt-created analytics marts.

---

## 📊 Dashboard Features

The dashboard currently provides:

### KPI Metrics

* Total Plays
* Total Users
* Total Songs
* Total Artists
* Listening Hours
* Average Daily Active Listeners
* Total Likes

### Charts

* Daily Active Listeners
* Top 10 Songs
* Top 10 Artists
* Genre Trends
* Top Users by Plays
* Listening Activity by Country
* Listening Activity by Device

### Interactive Filters

The dashboard includes filters for:

* Country
* Device
* Date Range

These filters allow users to explore the analytics interactively.

---

# 🔐 Security

Credentials are intentionally excluded from the repository.

The following files should **not** be committed:

```text
dbt_music/profiles.yml
streamlit_app/.streamlit/secrets.toml
.env
```

The project provides:

```text
streamlit_app/.streamlit/secrets.toml.example
```

as a template.

Before running the application, create your own:

```text
streamlit_app/.streamlit/secrets.toml
```

and provide your Snowflake credentials.

Never commit real passwords, tokens or API keys.

---

# 🚀 How to Run the Project

## Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/music-analytics-data-pipeline.git
```

```bash
cd music-analytics-data-pipeline
```

---

## Step 2 — Generate the data

```bash
python producer/generate_music_data.py
```

This creates the CSV files inside:

```text
data/
```

---

## Step 3 — Configure Snowflake

Create:

```text
MUSIC_ANALYTICS
```

with:

```text
RAW
STAGING
ANALYTICS
```

Create the RAW tables and internal stage.

Upload the CSV files and load them using `COPY INTO`.

---

## Step 4 — Configure dbt

Install:

```bash
pip install dbt-snowflake
```

Configure your local dbt:

```text
~/.dbt/profiles.yml
```

or use the appropriate local dbt profile configuration.

Then verify:

```bash
dbt debug
```

---

## Step 5 — Run dbt

From the dbt project directory:

```bash
cd dbt_music
```

Run:

```bash
dbt build
```

---

## Step 6 — Configure Streamlit

Create:

```text
streamlit_app/.streamlit/secrets.toml
```

using the example file as a template.

Add your own Snowflake credentials.

---

## Step 7 — Run Streamlit

```bash
cd streamlit_app
```

Then:

```bash
streamlit run app.py
```

The dashboard will open in your browser.

---

# 📈 Business Questions Answered

This project can answer questions such as:

### Song Performance

* Which songs have the most plays?
* Which songs have the most likes?
* How many unique listeners does each song have?

### Artist Performance

* Which artists receive the most plays?
* How many unique listeners does each artist have?
* How much listening time does each artist generate?

### Genre Analysis

* How does listening activity change by genre?
* Which genres receive the most plays?
* How does genre activity change over time?

### User Behavior

* Which users listen most frequently?
* How many unique songs does each user listen to?
* How much time do users spend listening?

### Engagement

* How many likes and skips are generated?
* How does engagement vary across songs and artists?

### Audience

* Which countries generate the most listening activity?
* Which devices are used most frequently?

---

# 🧠 Key Data Engineering Concepts Demonstrated

This project demonstrates practical knowledge of:

* Data generation
* Batch ingestion
* Snowflake internal stages
* Snowflake `COPY INTO`
* RAW data architecture
* ELT
* dbt sources
* dbt staging models
* dbt intermediate models
* dbt analytics marts
* `ref()` dependencies
* Data quality testing
* Primary key validation
* Referential integrity testing
* Accepted-value testing
* SQL aggregations
* Window/time-based analytics
* Cloud data warehouse concepts
* Data visualization
* Streamlit
* Git/GitHub
* Credential management

---

# 🔄 Current Architecture vs Future Architecture

The current project intentionally uses a simple batch ingestion approach:

```text
Python
 ↓
CSV
 ↓
Snowflake
 ↓
dbt
 ↓
Streamlit
```

A future version can introduce real-time/event-driven technologies:

```text
Python Event Generator
        ↓
Google Pub/Sub
        ↓
Streaming Processing
        ↓
Snowflake
        ↓
dbt
        ↓
Streamlit
```

Potential future enhancements include:

* Google Pub/Sub
* PySpark Structured Streaming
* Snowflake Snowpipe
* Snowflake Streams
* Snowflake Tasks
* Incremental dbt models
* Real-time dashboards
* Cloud deployment
* Automated CI/CD
* dbt documentation hosting
* Monitoring and alerting

---

# 🎯 Project Objective

The main objective of this project is to demonstrate how raw event data can be transformed into reliable, tested and business-ready analytics using a modern data engineering stack.

The project separates responsibilities clearly:

```text
Snowflake
    → Data storage and ingestion

dbt
    → Transformation and business logic

Streamlit
    → Visualization and user interaction
```

This separation makes the pipeline easier to maintain, test and extend.

---

# 👨‍💻 Author

**Your Name**

Data Engineering Portfolio Project

Technologies:

```text
Python | Snowflake | SQL | dbt | Streamlit | Git | GitHub
```

---

## ⭐ Future Improvements

Planned enhancements:

* Real-time event ingestion
* Pub/Sub integration
* Streaming processing
* Incremental dbt models
* Automated pipeline execution
* Data freshness monitoring
* CI/CD for dbt
* Dashboard deployment
* Advanced user segmentation
* Recommendation-system analytics
* Real-time alerts for unusual listening patterns
