import time
import json
import random
from datetime import datetime
from paho.mqtt import client as mqtt_client
import os

BROKER = os.getenv("MQTT_BROKER", "mqtt_broker")
PORT = int(os.getenv("MQTT_PORT", 1883))

def connect_mqtt():
    """Create and connect the MQTT client."""
    client = mqtt_client.Client("iot_data_gen")
    client.connect(BROKER, PORT)
    return client

def publish(client):
    """Continuously publish random sensor data to <location>/<station>."""
    while True:
        location = random.choice(["UPB", "Lab", "Office"])
        station = random.choice(["RPi_1", "ESP32", "Arduino"])
        payload = {
            "BAT": random.randint(10, 100),
            "TEMP": round(random.uniform(20.0, 35.0), 2),
            "HUMID": random.randint(30, 80),
            "timestamp": datetime.utcnow().isoformat()
        }
        topic = f"{location}/{station}"
        client.publish(topic, json.dumps(payload))
        print(f"Published {payload} to {topic}")
        time.sleep(2)

if __name__ == "__main__":
    client = connect_mqtt()
    publish(client)
