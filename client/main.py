from binascii import hexlify
from time import sleep
from umqtt.simple import MQTTClient
import json
import machine
import sensor
import struct


msg_buffer = bytearray(2)

def read_config():
    with open("config.json") as config_file:
        return json.load(config_file)   

def publish(client, topic, temp, hum):
    struct.pack_into("BB", msg_buffer, 0, temp, hum)
    client.publish(topic, msg_buffer)

config = read_config()
dht = sensor.create(config["model"], config["dhtPin"])

client_id = hexlify(machine.unique_id())
mqtt_client = MQTTClient(client_id, config["server"], keepalive=60)
mqtt_client.connect()

while True:
    temp, hum = sensor.measure(dht)
    print("temp:", temp)
    print("hum:", hum)
    publish(mqtt_client, config["topic"], temp, hum)
    sleep(60)
