import json
import os
import tempfile

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
    dir_path = os.path.dirname(DATA_PATH) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, DATA_PATH)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
