from machine import Pin

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
    sensor.measure()
    temp = sensor.temperature()
    humidity = sensor.humidity()
    return (int(temp), int(humidity))
