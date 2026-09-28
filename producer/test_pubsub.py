from google.cloud import pubsub_v1


PROJECT_ID = "project-b8fc8724-8adc-4499-9a4"
TOPIC_ID = "music-events"


publisher = pubsub_v1.PublisherClient()

topic_path = publisher.topic_path(
    PROJECT_ID,
    TOPIC_ID
)

message = "Hello from my music analytics pipeline"

data = message.encode("utf-8")

future = publisher.publish(
    topic_path,
    data
)

message_id = future.result()

print("Message published successfully!")
print("Message ID:", message_id)