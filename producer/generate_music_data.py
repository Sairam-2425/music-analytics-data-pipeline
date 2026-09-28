
import csv
import os
import random
from datetime import datetime, timedelta


# ============================================================
# CONFIGURATION
# ============================================================

NUM_USERS = 1000
NUM_ARTISTS = 100
NUM_SONGS = 500
NUM_EVENTS = 100000

OUTPUT_DIRECTORY = "../data"


# ============================================================
# MASTER DATA
# ============================================================

FIRST_NAMES = [
    "Rahul", "Arjun", "Priya", "Ananya", "Kiran",
    "Neha", "Ravi", "Sneha", "Aditya", "Pooja",
    "Vikram", "Meera", "Rohan", "Kavya", "Amit",
    "Divya", "Sanjay", "Nisha", "Varun", "Isha"
]

COUNTRIES = [
    "India",
    "USA",
    "UK",
    "Canada",
    "Australia"
]

DEVICES = [
    "mobile",
    "desktop",
    "tablet"
]

GENRES = [
    "Pop",
    "Rock",
    "Hip-Hop",
    "EDM",
    "Jazz",
    "Classical",
    "R&B",
    "Country"
]

EVENT_TYPES = [
    "play",
    "pause",
    "skip",
    "like"
]

ARTIST_FIRST_NAMES = [
    "Aria", "Leo", "Maya", "Noah", "Luna",
    "Ethan", "Zara", "Ryan", "Ava", "Liam",
    "Mia", "Kai", "Nora", "Eli", "Sofia"
]

ARTIST_LAST_NAMES = [
    "Music", "Stone", "Wave", "Sky", "Sound",
    "River", "Light", "Moon", "Star", "Beat"
]


# ============================================================
# HELPER FUNCTION
# ============================================================

def ensure_output_directory():
    """
    Create the output directory if it doesn't already exist.
    """

    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)


# ============================================================
# GENERATE USERS
# ============================================================

def generate_users():
    """
    Generate user master data.
    """

    users = []

    for i in range(1, NUM_USERS + 1):

        user = {
            "user_id": f"user_{i:05d}",
            "user_name": random.choice(FIRST_NAMES),
            "country": random.choice(COUNTRIES),
            "device": random.choice(DEVICES)
        }

        users.append(user)

    return users


# ============================================================
# GENERATE ARTISTS
# ============================================================

def generate_artists():
    """
    Generate artist master data.
    """

    artists = []

    for i in range(1, NUM_ARTISTS + 1):

        first_name = random.choice(ARTIST_FIRST_NAMES)
        last_name = random.choice(ARTIST_LAST_NAMES)

        artist = {
            "artist_id": f"artist_{i:04d}",
            "artist_name": f"{first_name} {last_name}",
            "genre": random.choice(GENRES)
        }

        artists.append(artist)

    return artists


# ============================================================
# GENERATE SONGS
# ============================================================

def generate_songs(artists):
    """
    Generate songs and associate each song with an artist.
    """

    songs = []

    for i in range(1, NUM_SONGS + 1):

        artist = random.choice(artists)

        duration = random.randint(120, 360)

        song = {
            "song_id": f"song_{i:05d}",
            "song_name": f"Song {i}",
            "artist_id": artist["artist_id"],
            "artist_name": artist["artist_name"],
            "genre": artist["genre"],
            "duration_seconds": duration
        }

        songs.append(song)

    return songs


# ============================================================
# GENERATE MUSIC EVENTS
# ============================================================

def generate_music_events(users, songs):
    """
    Generate music listening events.
    """

    events = []

    start_time = datetime.now() - timedelta(days=30)

    for i in range(1, NUM_EVENTS + 1):

        user = random.choice(users)
        song = random.choice(songs)

        event_type = random.choices(
            EVENT_TYPES,
            weights=[70, 10, 10, 10],
            k=1
        )[0]

        event_time = (
            start_time +
            timedelta(
                seconds=random.randint(
                    0,
                    30 * 24 * 60 * 60
                )
            )
        )

        # For play events, use a realistic listening duration.
        if event_type == "play":
            duration = random.randint(
                30,
                song["duration_seconds"]
            )

        elif event_type == "pause":
            duration = random.randint(
                10,
                song["duration_seconds"]
            )

        elif event_type == "skip":
            duration = random.randint(
                5,
                min(60, song["duration_seconds"])
            )

        else:
            duration = 0

        event = {
            "event_id": f"evt_{i:08d}",
            "user_id": user["user_id"],
            "song_id": song["song_id"],
            "song_name": song["song_name"],
            "artist_id": song["artist_id"],
            "artist_name": song["artist_name"],
            "genre": song["genre"],
            "event_type": event_type,
            "duration_seconds": duration,
            "device": user["device"],
            "country": user["country"],
            "timestamp": event_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        events.append(event)

    return events


# ============================================================
# WRITE CSV
# ============================================================

def write_csv(filename, data, fieldnames):

    filepath = os.path.join(
        OUTPUT_DIRECTORY,
        filename
    )

    with open(
        filepath,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(data)

    print(
        f"Created: {filepath} "
        f"({len(data)} records)"
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 60)
    print("MUSIC ANALYTICS DATA GENERATOR")
    print("=" * 60)

    ensure_output_directory()

    # --------------------------------------------------------
    # 1. Generate users
    # --------------------------------------------------------

    print("\nGenerating users...")

    users = generate_users()

    write_csv(
        "users.csv",
        users,
        [
            "user_id",
            "user_name",
            "country",
            "device"
        ]
    )

    # --------------------------------------------------------
    # 2. Generate artists
    # --------------------------------------------------------

    print("\nGenerating artists...")

    artists = generate_artists()

    write_csv(
        "artists.csv",
        artists,
        [
            "artist_id",
            "artist_name",
            "genre"
        ]
    )

    # --------------------------------------------------------
    # 3. Generate songs
    # --------------------------------------------------------

    print("\nGenerating songs...")

    songs = generate_songs(artists)

    write_csv(
        "songs.csv",
        songs,
        [
            "song_id",
            "song_name",
            "artist_id",
            "artist_name",
            "genre",
            "duration_seconds"
        ]
    )

    # --------------------------------------------------------
    # 4. Generate music events
    # --------------------------------------------------------

    print("\nGenerating music events...")

    events = generate_music_events(
        users,
        songs
    )

    write_csv(
        "music_events.csv",
        events,
        [
            "event_id",
            "user_id",
            "song_id",
            "song_name",
            "artist_id",
            "artist_name",
            "genre",
            "event_type",
            "duration_seconds",
            "device",
            "country",
            "timestamp"
        ]
    )

    # --------------------------------------------------------
    # Finished
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETED")
    print("=" * 60)

    print(f"Users generated   : {len(users)}")
    print(f"Artists generated : {len(artists)}")
    print(f"Songs generated   : {len(songs)}")
    print(f"Events generated  : {len(events)}")

    print(
        f"\nFiles are available in: "
        f"{OUTPUT_DIRECTORY}"
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()

