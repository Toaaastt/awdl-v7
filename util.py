import json
from typing import Any

def write_json_file(data, filename='settings.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, sort_keys=True)


def read_json_file(filename='settings.json') -> dict[str, Any]:
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def cursor_up(n=1):
    print(f"\033[{n}A", end='')