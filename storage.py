import json
import os

DATA_PATH = os.path.expanduser("~/.hostel.json")


def _default_data():
    return {
        "rooms": {},
        "beds": {},
        "checkins": [],
    }


def load():
    if not os.path.exists(DATA_PATH):
        return _default_data()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
