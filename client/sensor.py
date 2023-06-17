from machine import Pin
from time import time


def create(model, pin):
    if model == "dht11":
        from dht import DHT11

        return DHT11(Pin(pin))
    elif model == "dht22":
        from dht import DHT22

        return DHT22(Pin(pin))
    else:
        raise ValueError(f"unknown sensor model: {model}")


def measure(sensor):
    # micropython/python epoch diff 1970/2000
    # make it into a regular unix timestamp
    epoch_diff = const(946684800)
    timestamp = time() + epoch_diff
    sensor.measure()
    temp = sensor.temperature()
    humidity = sensor.humidity()
    return (int(timestamp), int(temp), int(humidity))
