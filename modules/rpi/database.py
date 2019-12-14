from typing import Tuple, Optional

import pymongo.errors
import tinydb

from modules.rpi import data
from modules.rpi import vision
from modules.utils import info

mongo_remote_url = f"mongodb://{data.config['mongo']['username']}:{data.config['mongo']['password']}@" \
                   f"{data.config['mongo']['host']}:{data.config['mongo']['port']}"

students_col: pymongo.collection.Collection
reports_col: pymongo.collection.Collection

is_connected_mongo = False

students_info = tinydb.TinyDB(data.KNOWN_FACES_INFO_PATH)


def connect_to_mongo():
    global is_connected_mongo
    global students_col
    global reports_col
    info("[Database] Attempting to connect to the Mongo database.")
    success, remote_db = get_mongo_client(mongo_remote_url)
    if success:
        remote_db = remote_db.get_database("class-attendance-tracker")
        students_col = remote_db.get_collection("students")
        reports_col = remote_db.get_collection("reports")
        info("[Database] Mongo database connection is successful.")
    else:
        info("[Database] Mongo database connection is failed.")
    is_connected_mongo = success


def get_mongo_client(url) -> Tuple[bool, Optional[pymongo.MongoClient]]:
    try:
        client = pymongo.MongoClient(url, tz_aware=True)
        client.server_info()
        return True, client
    except pymongo.errors.ServerSelectionTimeoutError:
        return False, None


def sync_database():
    success, client = get_mongo_client(mongo_remote_url)
    info("[Database] Syncing the local database.")
    if not success:
        info("[Database] Cannot sync the local database, server is unavailable.")
        return
    db = client.get_database("class-attendance-tracker")
    students_collection = db.get_collection("students")
    ids = []
    for student in students_collection.find({}, {"face": 0}):
        inserted_id = str(student['_id'])
        res = students_info.search(tinydb.where('inserted-id') == inserted_id)
        ids.append(inserted_id)
        if len(res) == 1:
            continue
        info(f"[Database] Adding a new student to the database with id {student['id']}.")
        face = students_collection.find_one({'_id': student['_id']}, {"face": 1})['face']
        face = vision.Frame.open_bytes(face)
        relative_path = f"{inserted_id}.jpg"
        face.save(f"{data.KNOWN_FACES_PATH}/{relative_path}")
        students_info.insert({
            'inserted-id': inserted_id,
            'id': student['id'],
            'name': student['name'],
            'classroom': student['classroom'],
            'face-path': relative_path
        })
    for student in students_info.all():
        if student['inserted-id'] not in ids:
            students_info.remove(tinydb.where('inserted-id') == student['inserted-id'])
            info(f"[Database] Student with id {student['id']} is removed from the local database.")
    info("[Database] Synchronization finished.")
