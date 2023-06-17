from binascii import hexlify
from time import sleep
from umqtt.simple import MQTTClient
import json
import machine
import ntptime
import sensor
import struct


msg_buffer = bytearray(6)


def read_config():
    with open("config.json") as config_file:
        return json.load(config_file)


def publish(client, topic, timestamp, temp, hum):
    struct.pack_into("!IBB", msg_buffer, 0, timestamp, temp, hum)
    client.publish(topic, msg_buffer)


def main():
    ntptime.settime()

    config = read_config()
    dht = sensor.create(config["model"], config["dhtPin"])

    client_id = hexlify(machine.unique_id())
    mqtt_client = MQTTClient(client_id, config["server"], keepalive=60)
    mqtt_client.connect()

    while True:
        timestamp, temp, hum = sensor.measure(dht)
        print("time:", timestamp)
        print("temp:", temp)
        print("hum:", hum)
        publish(mqtt_client, config["topic"], timestamp, temp, hum)
        sleep(20)


if __name__ == "__main__":
    main()
