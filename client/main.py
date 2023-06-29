from binascii import hexlify
from time import sleep, time
from umqtt.simple import MQTTClient
import json
import machine
import ntptime
import sensor
import struct

# How often to measure in seconds
PERIOD = const(15 * 60)


msg_buffer = bytearray(6)


def read_config():
    with open("config.json") as config_file:
        return json.load(config_file)


def publish(client, topic, timestamp, temp, hum):
    struct.pack_into("!IBB", msg_buffer, 0, timestamp, temp, hum)
    client.publish(topic, msg_buffer)


def wait_for_period(early=0):
    seconds_to_period = PERIOD - (time() % PERIOD) - early
    if seconds_to_period > 0:
        print(f"sleeping for {seconds_to_period} seconds (early = {early})")
        sleep(seconds_to_period)


def perform_measurement(client_id, server, topic, dht):
    mqtt_client = MQTTClient(client_id, server, keepalive=60)
    mqtt_client.connect()

    # now when the MQTT client is connected, let's wait the final seconds
    wait_for_period()

    timestamp, temp, hum = sensor.measure(dht)
    print("time:", timestamp)
    print("temp:", temp)
    print("hum:", hum)
    publish(mqtt_client, topic, timestamp, temp, hum)

    # wait for network stack to do its thing

    mqtt_client.disconnect()

    sleep(10)


def main():
    ntptime.settime()

    config = read_config()

    client_id = hexlify(machine.unique_id())
    server = config["server"]
    topic = config["topic"] + "/" + client_id.decode("UTF-8")
    dht = sensor.create(config["model"], config["dhtPin"])

    # wait until it is almost time to measure
    wait_for_period(early=60)

    try:
        perform_measurement(client_id, server, topic, dht)
    except Exception as ex:
        # if there is an exception just log it and go to
        # sleep and retry next period
        print("unable to perform measurement", ex)

    # Sleep for slightly shorter than the period. To save power and
    # have some slack to be able to connect to the network, mqtt etc.
    # upon reset

    print("going into deep sleep")

    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, (PERIOD - 90) * 1000)

    machine.deepsleep()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as ex:
            print("Exception in main", ex)
