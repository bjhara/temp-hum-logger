from typing import List, Tuple
import sqlite3

_measurements_table_name = "measurements"
_write_conn: sqlite3.Connection | None = None
_read_conn: sqlite3.Connection | None = None
_write_cur: sqlite3.Cursor | None = None
_read_cur: sqlite3.Cursor | None = None


def setup() -> None:
    global _write_conn
    global _write_cur
    global _read_cur

    # it should be safe to set check_same_thread=False since we only
    # write to the database on incoming messages, which should be handled
    # by a single thread
    _write_conn = sqlite3.connect("measurements.db", check_same_thread=False)
    _read_conn = sqlite3.connect("measurements.db", check_same_thread=False)
    _write_cur = _write_conn.cursor()
    _read_cur = _read_conn.cursor()

    res = _write_cur.execute(
        f"SELECT name FROM sqlite_master WHERE name=:name",
        {"name": _measurements_table_name},
    )
    if res.fetchone() is None:
        print(f"Creating table {_measurements_table_name}")
        _write_cur.execute(
            f"""CREATE TABLE {_measurements_table_name} (
                                client_id TEXT,
                                timestamp INTEGER, 
                                temp INTEGER, 
                                hum INTEGER,
                                PRIMARY KEY(client_id, timestamp)
                          )"""
        )


def shutdown() -> None:
    if _write_conn is not None:
        _write_conn.close()

    if _read_conn is not None:
        _read_conn.close()


def add_measurement(client_id: str, timestamp: int, temp: int, hum: int) -> None:
    if _write_cur is None or _write_conn is None:
        raise Exception("no db connection")

    _write_cur.execute(
        f"INSERT INTO {_measurements_table_name} VALUES (:client_id, :timestamp, :temp, :hum)",
        {
            "client_id": client_id,
            "timestamp": timestamp,
            "temp": temp,
            "hum": hum,
        },
    )
    _write_conn.commit()


def get_measurements(client_id: str) -> List[Tuple[int, int, int]]:
    if _read_cur is None:
        raise Exception("no db connection")

    res = _read_cur.execute(
        f"""SELECT timestamp, temp, hum 
            FROM {_measurements_table_name} 
            WHERE client_id=?
            ORDER BY timestamp ASC""",
        (client_id,),
    )
    return res.fetchall()


def get_clients() -> List[str]:
    if _read_cur is None:
        raise Exception("no db connection")

    res = _read_cur.execute(
        f"SELECT DISTINCT client_id FROM {_measurements_table_name}",
    )
    return [client_id for (client_id,) in res.fetchall()]


if __name__ == "__main__":
    setup()
    clients = get_clients()
    print(clients)
    for client_id in clients:
        print(get_measurements(client_id))
