import json
import time
import random
import uuid
from kafka import KafkaProducer  # Uncommented


def generate_ride():
    return {
        "ride_id": str(uuid.uuid4()),
        "latitude": round(random.uniform(40.7, 40.8), 6),
        "longitude": round(random.uniform(-74.0, -73.9), 6),
        "timestamp": time.time(),
        "distance_km": round(random.uniform(0.5, 20.0), 2),
        "traffic_multiplier": round(random.uniform(1.0, 2.0), 2)
    }


def run():
    print("🚕 Taxi Ride Generator Started...")

    # Initialize the Producer
    producer = KafkaProducer(
        bootstrap_servers='localhost:9093',  # 9093 for local dev
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    try:
        while True:
            ride = generate_ride()
            print(f"Sending: {ride['ride_id']}")  # Print ID just to see activity

            # Send to topic 'ride_requests'
            producer.send('ride_requests', ride)

            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 Stopping generator...")


if __name__ == "__main__":
    run()