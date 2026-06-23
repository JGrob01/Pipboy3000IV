import json
import os

_SELECTION_FILE = "selections.json"
_data = {}


def load():
    global _data
    if os.path.exists(_SELECTION_FILE):
        try:
            with open(_SELECTION_FILE, "r") as f:
                _data = json.load(f)
        except Exception as e:
            print("Failed to load selections:", e)
            _data = {}
    else:
        _data = {}


def save():
    try:
        with open(_SELECTION_FILE, "w") as f:
            json.dump(_data, f, indent=2)
    except Exception as e:
        print("Failed to save selections:", e)


def is_selected(submenu_key, index):
    return index in _data.get(submenu_key, [])


def toggle(submenu_key, index, mode="single"):
    current = set(_data.get(submenu_key, []))
    if mode == "single":
        current = set() if index in current else {index}
    else:  # multi
        current.discard(index) if index in current else current.add(index)
    _data[submenu_key] = sorted(current)
    save()
    return current