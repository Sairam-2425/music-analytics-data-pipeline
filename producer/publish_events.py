import csv
import time

from google.cloud import pubsub_v1


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ID = "project-b8fc8724-8adc-4499-9a4"
TOPIC_ID = "music-events"

CSV_FILE = "../data/music_events.csv"

# Time between events
DELAY_SECONDS = 0


# ============================================================
# CREATE PUB/SUB CLIENT
# ============================================================

publisher = pubsub_v1.PublisherClient()

topic_path = publisher.topic_path(
    PROJECT_ID,
    TOPIC_ID
)


# ============================================================
# PUBLISH EVENTS
# ============================================================

def publish_events():

    print("=" * 60)
    print("MUSIC EVENT PUBLISHER")
    print("=" * 60)

    print(f"Reading file: {CSV_FILE}")
    print(f"Publishing to: {topic_path}")

    published_count = 0

    with open(
        CSV_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            # Convert the CSV row back into CSV format
            message = ",".join(row.values())

            # Convert string to bytes
            data = message.encode("utf-8")

            # Publish message
            future = publisher.publish(
                topic_path,
                data
            )

            # Wait for Pub/Sub confirmation
            message_id = future.result()

            published_count += 1

            print(
                f"Published event "
                f"{row['event_id']} "
                f"| Message ID: {message_id}"
            )

            # Simulate streaming
            time.sleep(DELAY_SECONDS)

    print("\n" + "=" * 60)
    print("PUBLISHING COMPLETED")
    print("=" * 60)

    print(f"Total events published: {published_count}")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    publish_events()