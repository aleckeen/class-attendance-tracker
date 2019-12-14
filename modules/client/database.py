import pymongo.errors

from modules.client import data

mongo_remote_url = f"mongodb://{data.config['mongo']['username']}:{data.config['mongo']['password']}@" \
                   f"{data.config['mongo']['host']}:{data.config['mongo']['port']}"

students_col: pymongo.collection.Collection
reports_col: pymongo.collection.Collection

is_connected_mongo = False


def connect_to_mongo():
    global is_connected_mongo
    global students_col
    global reports_col
    print("[Database] Attempting to connect to the Mongo database.")
    try:
        remote_db = pymongo.MongoClient(mongo_remote_url, tz_aware=True)
        remote_db.server_info()
        is_connected_mongo = True
        remote_db = remote_db.get_database("class-attendance-tracker")
        students_col = remote_db.get_collection("students")
        reports_col = remote_db.get_collection("reports")
        print("[Database] Mongo database connection is successful.")
    except pymongo.errors.ServerSelectionTimeoutError:
        is_connected_mongo = False
        print("[Database] Mongo database connection is failed.")


connect_to_mongo()
