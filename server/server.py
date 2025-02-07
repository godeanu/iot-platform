import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WriteOptions
from datetime import datetime
import json
import os
import logging

DEBUG_MODE = os.getenv("DEBUG_DATA_FLOW", "false").lower() == "true"
BROKER = os.getenv("BROKER", "mqtt_broker")
BROKER_PORT = int(os.getenv("MQTT_PORT", 1883))
INFLUXDB_URL = "http://influxdb:8086"
INFLUXDB_TOKEN = os.getenv("INFLUXDB", "my-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "my-org")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "iot_data")

if DEBUG_MODE:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

influx_client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)

#batch_size=1 to write each point individually immediately
write_api = influx_client.write_api(write_options=WriteOptions(batch_size=1))

def on_connect(client, userdata, flags, rc):
    logging.debug(f"Connected to MQTT broker with result code [{rc}]")
    client.subscribe("#")

def on_message(client, userdata, msg):
    topic_str = msg.topic

    if DEBUG_MODE:
        logging.info(f"Received a message by topic [{topic_str}]")

    # check if the topic is in the format "location/station"
    if topic_str.count("/") != 1:
        logging.debug(f"Skipping message with invalid topic [{topic_str}]")
        return

    #split the topic into location and station
    parts = topic_str.split("/", 1)
    if len(parts) != 2 or not all(parts):
        logging.debug(f"Topic missing location/station [{topic_str}]")
        return

    location, station = parts

    try:
        data = json.loads(msg.payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logging.debug(f"Invalid JSON payload for topic [{topic_str}]: {e}")
        return

    # if the payload has a timestamp, use it; otherwise, use the current time
    raw_ts = data.get("timestamp")
    if raw_ts:
        try:
            parsed_ts = datetime.fromisoformat(raw_ts)
            if DEBUG_MODE:
                logging.info(f"Data timestamp is: {parsed_ts}")
        except ValueError:
            parsed_ts = datetime.utcnow()
            if DEBUG_MODE:
                logging.info("Data timestamp is NOW (invalid format in payload)")
    else:
        parsed_ts = datetime.utcnow()
        if DEBUG_MODE:
            logging.info("Data timestamp is NOW (no 'timestamp' key)")

    # filter out non-numeric fields
    numeric_fields = {
        k: v for k, v in data.items() if isinstance(v, (int, float))
    }
    if not numeric_fields:
        logging.debug(f"No numeric fields in payload for [{topic_str}]")
        return

    measurement_name = f"{location}.{station}"

    for field_name, field_value in numeric_fields.items():
        point = (
            Point(measurement_name)
            .tag("location", location)
            .tag("station", station)
            .field(field_name, field_value)
            .time(parsed_ts)
        )

        if DEBUG_MODE:
            logging.info(f"{measurement_name}.{field_name} {field_value}")

        try:
            write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        except Exception as e:
            logging.warning(
                f"Failed to write field [{field_name}] "
                f"for topic [{topic_str}]: {e}"
            )

def main():
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, BROKER_PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()
