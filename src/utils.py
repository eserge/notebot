import json
from datetime import datetime


DATETIME_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class JsonDumps(json.JSONEncoder):
    def default(self, val):
        if isinstance(val, datetime):
            return val.strftime(DATETIME_ISO_FORMAT)

        return super().default(val)
