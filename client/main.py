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
# How early we need to wake up to be certain to connect,
# set the time and get ready to measure.
BUFFER_TIME = const(20)

msg_buffer = bytearray(6)


def deep_sleep(time_ms):
    print("going into deep sleep")

    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, time_ms)

    machine.deepsleep()


def read_config():
    with open("config.json") as config_file:
        return json.load(config_file)


def publish(client, topic, timestamp, temp, hum):
    struct.pack_into("!IBB", msg_buffer, 0, timestamp, temp, hum)
    client.publish(topic, msg_buffer)


def wait_for_period(early=0):
    seconds_to_period = PERIOD - (time() % PERIOD) - early
    # deep sleep does not seem to be that exact so let's not
    # use it if we need to hit the target with some precision
    if seconds_to_period > BUFFER_TIME and early > 0:
        print(f"deep sleeping for {seconds_to_period} seconds (early = {early})")
        deep_sleep(seconds_to_period * 1000)
    elif seconds_to_period > 0:
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

    # wait until it is almost time to measure
    wait_for_period(early=BUFFER_TIME)

    config = read_config()

    client_id = hexlify(machine.unique_id())
    server = config["server"]
    topic = config["topic"] + "/" + client_id.decode("UTF-8")
    dht = sensor.create(config["model"], config["dhtPin"])

    try:
        perform_measurement(client_id, server, topic, dht)
    except Exception as ex:
        # if there is an exception just log it and go to
        # sleep and retry next period
        print("unable to perform measurement", ex)

    # Sleep for slightly shorter than the period. To save power and
    # have some slack to be able to connect to the network, mqtt etc.
    # upon reset. Long deep sleeps seem to be quite inexact.

    deep_sleep((PERIOD - 2 * BUFFER_TIME) * 1000)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as ex:
            print("Exception in main", ex)
