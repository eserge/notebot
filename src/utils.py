import json
from datetime import datetime
from typing import Dict

from pydantic import BaseModel

DATETIME_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class JsonDumps(json.JSONEncoder):
    def default(self, val):
        if isinstance(val, datetime):
            return val.strftime(DATETIME_ISO_FORMAT)
        if isinstance(val, BaseModel):
            return json.dumps(val.dict())

        return super().default(val)


def json_dumps(data: Dict) -> str:
    return json.dumps(data, cls=JsonDumps, indent=2)
