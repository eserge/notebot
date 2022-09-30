import os
import json
from typing import Dict, Optional

from config import get_settings


DATA_FILENAME = "tokens.json"


def _load_token_data() -> Optional[Dict[str, str]]:
    settings = get_settings()
    dirname = settings.app_data_dir
    filename = os.path.join(dirname, DATA_FILENAME)
    if not os.path.exists(filename):
        return None

    try:
        with open(filename, mode="r") as f:
            token_data = json.load(f)
    except (OSError, ValueError):
        return None

    return token_data or None


def get_token(user_id: str) -> Optional[str]:
    token_data = _load_token_data()
    return token_data.get(user_id)
