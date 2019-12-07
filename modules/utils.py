import datetime
from typing import Optional

import pytz
import tinydb

tz = pytz.UTC
log_db: Optional[tinydb.TinyDB] = None


def info(msg: str):
    timestamp = datetime.datetime.now(tz=tz)
    print(f"{timestamp} [INFO] {msg}")
    if log_db is not None:
        log_db.insert({"timestamp": str(timestamp), "msg": msg})
