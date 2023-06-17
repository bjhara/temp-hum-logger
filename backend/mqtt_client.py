import database
import paho.mqtt.client as mqtt
import struct


_client: mqtt.Client | None = None


def get_client_from_topic(topic: str) -> str:
    parts = topic.rsplit("/", 1)
    if len(parts) == 2:
        return parts[1]
    else:
        raise ValueError(f"not a correct topic {topic}")


def on_connect(client, userdata, flags, rc) -> None:
    print("Connected with result code " + str(rc))
    client.subscribe("test_topic/+")


def on_message(client, userdata, msg) -> None:
    if len(msg.payload) == 6:
        timestamp, temp, hum = struct.unpack("!IBB", msg.payload)
        client_id = get_client_from_topic(msg.topic)
        database.add_measurement(client_id, timestamp, temp, hum)


def setup() -> None:
    global _client

    _client = mqtt.Client()
    _client.on_connect = on_connect
    _client.on_message = on_message

    _client.connect("localhost", 1883, 60)

    _client.loop_start()


def shutdown() -> None:
    if _client is not None:
        _client.loop_stop()
