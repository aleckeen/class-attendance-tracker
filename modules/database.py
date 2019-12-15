from typing import Tuple, Optional

import pymongo.errors
import pymongo.database


def get_mongo_client(url) -> Tuple[bool, Optional[pymongo.database.Database]]:
    try:
        client = pymongo.MongoClient(url, tz_aware=True)
        client.server_info()
        db = client.get_database("class-attendance-tracker")
        return True, db
    except pymongo.errors.ServerSelectionTimeoutError:
        return False, None
