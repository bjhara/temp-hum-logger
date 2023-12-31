from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import database
import mqtt_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.setup()
    mqtt_client.setup()
    yield
    mqtt_client.shutdown()
    database.shutdown()


app = FastAPI(lifespan=lifespan)

app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")


@app.get("/")
async def root():
    return RedirectResponse("/ui/")


@app.get("/clients")
async def clients() -> object:
    clients = database.get_clients()
    return clients


@app.get("/clients/{client_id}")
async def client_id(client_id: str) -> object:
    def round_minute(timestamp: int) -> int:
        seconds = timestamp % 60

        if seconds <= 30:
            return timestamp - seconds
        else:
            return timestamp + (60 - seconds)

    measurements = database.get_measurements(client_id)
    measurement_objects = [
        {
            "timestamp": round_minute(ts),
            "temp": temp,
            "hum": hum,
        }
        for (ts, temp, hum) in measurements
    ]
    return measurement_objects
