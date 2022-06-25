import json, subprocess

class Helper:
    def __init__(self):
        pass

    def parse_json(self, json_str):
        return json.loads(json_str)

helper = Helper()