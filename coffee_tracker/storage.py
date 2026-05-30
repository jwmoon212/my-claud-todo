import json
import os
import sys
from datetime import datetime, date

if getattr(sys, "frozen", False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(_BASE_DIR, "data", "coffee_log.json")

DEFAULT_DATA = {
    "daily_goal": None,
    "entries": []
}


def _load():
    if not os.path.exists(DATA_FILE):
        return dict(DEFAULT_DATA)
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _save(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_entry(note=""):
    data = _load()
    existing_ids = [e["id"] for e in data["entries"]]
    new_id = max(existing_ids, default=0) + 1
    entry = {
        "id": new_id,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "note": note
    }
    data["entries"].append(entry)
    _save(data)
    return entry, data["daily_goal"]


def delete_entry(entry_id):
    data = _load()
    before = len(data["entries"])
    data["entries"] = [e for e in data["entries"] if e["id"] != entry_id]
    if len(data["entries"]) == before:
        return False
    _save(data)
    return True


def get_entries_for_date(target_date):
    data = _load()
    return [
        e for e in data["entries"]
        if e["timestamp"].startswith(target_date.strftime("%Y-%m-%d"))
    ]


def get_entries_for_range(start_date, end_date):
    data = _load()
    results = {}
    current = start_date
    while current <= end_date:
        day_str = current.strftime("%Y-%m-%d")
        results[day_str] = [e for e in data["entries"] if e["timestamp"].startswith(day_str)]
        current = date.fromordinal(current.toordinal() + 1)
    return results


def set_goal(cups):
    data = _load()
    data["daily_goal"] = cups
    _save(data)


def get_goal():
    return _load().get("daily_goal")
