from time import sleep
import sensor
import json

def read_config():
  
    with open("config.json") as config_file:
        return json.load(config_file)   

config = read_config()
dht = sensor.create(config["model"], config["dhtPin"])

while True:
    temp, hum = sensor.measure(dht)
    print("temp:", temp)
    print("hum:", hum)
    sleep(60)
