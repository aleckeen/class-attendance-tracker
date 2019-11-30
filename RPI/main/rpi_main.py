import time

import io
import json
import os
import threading

import bson
import datetime
from enum import Enum, auto

from typing import List, Any, Dict

import pytz
import vision
import pymongo.errors
import tinydb
import networking


class Job(Enum):
    UPDATE_DATABASE = auto()
    UPDATE_RECOGNIZER = auto()
    SCAN_FACE = auto()
    DETECT_STUDENTS = auto()
    REPORT = auto()
    SHUTDOWN = auto()


CURRENT_JOB = Job.DETECT_STUDENTS
MONGO_CONNECTION_PATH = "../data/config/remote_mongo_connection.json"
CENTRAL_CONNECTION_PATH = "../data/config/central_server_connection.json"
PROJECT_SETTINGS_PATH = "../data/config/project.json"
PI_CONFIG_PATH = "../data/config/pi.json"
STUDENT_FACES_PATH = "../data/student_faces"
RECOGNITION_DATA_PATH = "../data/recognition_data"

with open(PROJECT_SETTINGS_PATH) as f:
    project = json.load(f)

with open(PI_CONFIG_PATH) as f:
    pi_config = json.load(f)

with open(MONGO_CONNECTION_PATH) as f:
    config = json.load(f)
    mongo_remote_url = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}"

with open(CENTRAL_CONNECTION_PATH) as f:
    config = json.load(f)
    address = (config['host'], config['port'], config['username'], config['password'])

STUDENT_FACES_PATH += f"/{project['sub-name']}"
STUDENTS_INFO_PATH = f"{STUDENT_FACES_PATH}/info.json"
RECOGNITION_DATA_PATH += f"/{project['sub-name']}"

if not os.path.isdir(STUDENT_FACES_PATH):
    os.mkdir(STUDENT_FACES_PATH)
if not os.path.isdir(RECOGNITION_DATA_PATH):
    os.mkdir(RECOGNITION_DATA_PATH)

CONNECTED_TO_MONGO = False
CONNECTED_TO_SERVER = False

students_col: pymongo.collection.Collection
reports_col: pymongo.collection.Collection


class Client(networking.client.Client):
    def connection_broke(self):
        global CONNECTED_TO_SERVER
        CONNECTED_TO_SERVER = False


client = Client.create()

students_info = tinydb.TinyDB(STUDENTS_INFO_PATH)
tz = pytz.timezone(project['timezone'])

camera = vision.vision.CameraFeed.create_picamera()
recognizer: vision.vision.FaceRecognizer

reports: List[Dict[str, Any]] = []


def info(msg: str):
    print(f"{datetime.datetime.now(tz=tz)} [INFO] {msg}")


def connect_to_mongo():
    global CONNECTED_TO_MONGO
    global students_col
    global reports_col
    try:
        remote_db = pymongo.MongoClient(mongo_remote_url, tz_aware=True)
        remote_db.server_info()
        CONNECTED_TO_MONGO = True
        remote_db = remote_db.get_database(project['sub-name'])
        students_col = remote_db.get_collection("students")
        reports_col = remote_db.get_collection("reports")
        info("Mongo connection is successful")
    except pymongo.errors.ServerSelectionTimeoutError:
        CONNECTED_TO_MONGO = False
        info("Mongo connection is failed")


def connect_to_central():
    global CONNECTED_TO_SERVER
    global client
    client = Client.create()
    status = client.connect(address[0], address[1])
    if status == networking.client.ConnectionStatus.CONNECTION_FAILED:
        CONNECTED_TO_SERVER = False
        return
    client.send(address[2])
    client.send(address[3])
    res = client.recv()
    if res != "OK":
        CONNECTED_TO_SERVER = False
        return
    client.send("CAMERA")
    client.send(pi_config['pi-id'])
    client.send(pi_config['location'])
    CONNECTED_TO_SERVER = True


def start_central():
    if CONNECTED_TO_SERVER:
        def recv_continuous(self):
            global CURRENT_JOB
            while True:
                if CURRENT_JOB == Job.SCAN_FACE:
                    time.sleep(0.25)
                    continue
                req = self.recv()
                if req is None:
                    break
                elif req == "SCAN":
                    CURRENT_JOB = Job.SCAN_FACE
                elif req == "ALIVE":
                    client.send("OK")

        t = threading.Thread(target=recv_continuous, args=[client])
        t.daemon = True
        t.start()


def update_database():
    if not CONNECTED_TO_MONGO:
        info("Cannot update database central server is unavailable")
        return
    info("Updating the local database")
    ids = []
    for student in students_col.find({}, {"face": 0}):
        inserted_id = str(student['_id'])
        res = students_info.search(tinydb.where('inserted-id') == inserted_id)
        ids.append(inserted_id)
        if len(res) == 1:
            continue
        info(f"Adding new student to the database with id {student['id']}")
        face = students_col.find_one({'_id': student['_id']}, {"face": 1})['face']
        face = vision.vision.Frame.open_bytes(face)
        relative_path = f"{inserted_id}.jpg"
        face.save(f"{STUDENT_FACES_PATH}/{relative_path}")
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
            info(f"Student with id {student['id']} is removed from the local database")
    info("Update finished")


def update_recognizer():
    global recognizer
    faces: List[vision.vision.Frame] = []
    ids: List[str] = []
    for student in students_info.all():
        frame = vision.vision.Frame.open_path(f"{STUDENT_FACES_PATH}/{student['face-path']}")
        faces.append(frame)
        ids.append(student['inserted-id'])
    recognizer = vision.vision.FaceRecognizer(faces, ids)


def scan_face():
    global CURRENT_JOB
    while True:
        frame = camera.capture()
        frame.flip(h=True, v=True)
        info("Image has been taken")
        faces = vision.vision.FaceDetector.ageitgey(frame)
        if len(faces) != 1:
            info("Detection failure")
            continue
        info("Successful")
        break
    client.send("OK")
    student_id = client.recv()
    student_name = client.recv()
    classroom = client.recv()
    face_bin = io.BytesIO()
    faces[0].write(face_bin, ".jpg")
    student = {
        "id": student_id,
        "name": student_name,
        "classroom": classroom,
        "face": face_bin.getvalue()
    }
    students_col.insert_one(student)
    if CURRENT_JOB == Job.SCAN_FACE:
        CURRENT_JOB = Job.DETECT_STUDENTS


def detect_students():
    info(str(len(reports)))
    frame = camera.capture()
    info("Frame taken for processing")
    frame.flip(h=True, v=True)
    faces = vision.vision.FaceDetector.opencv(frame)
    info(f"Found {len(faces)} faces")
    for student_id, face in recognizer.recognize(faces):
        if student_id == -1:
            student_id = "unknown"
        elif not student_id:
            student_id = "recognition-failure"
        else:
            student_id = bson.ObjectId(student_id)
        timestamp = datetime.datetime.now(tz=tz)
        reports.append({
            "pi-id": pi_config["pi-id"],
            "location": pi_config["location"],
            "student-id": student_id,
            "timestamp": timestamp
        })
        info(f"Recognized student with id {student_id}")
        path = f"{RECOGNITION_DATA_PATH}/{student_id}"
        if not os.path.isdir(path):
            os.mkdir(path)
        face.save(f"{path}/{timestamp}.jpg")


def report():
    global reports
    if len(reports) == 0 or not CONNECTED_TO_MONGO:
        return
    info("Reporting")
    reports_col.insert_many(reports)
    reports = []


def shutdown():
    info("Exiting")
    report()


def main():
    global CURRENT_JOB
    while True:
        if len(reports) > 10 and CONNECTED_TO_MONGO and CURRENT_JOB != Job.REPORT:
            CURRENT_JOB = Job.REPORT
        elif CURRENT_JOB == Job.DETECT_STUDENTS:
            detect_students()
        elif CURRENT_JOB == Job.UPDATE_DATABASE:
            update_database()
        elif CURRENT_JOB == Job.UPDATE_RECOGNIZER:
            update_recognizer()
        elif CURRENT_JOB == Job.REPORT:
            report()
            if CURRENT_JOB == Job.REPORT:
                CURRENT_JOB = Job.DETECT_STUDENTS
        elif CURRENT_JOB == Job.SCAN_FACE:
            scan_face()
        elif CURRENT_JOB == Job.SHUTDOWN:
            shutdown()
            break


if __name__ == '__main__':
    try:
        connect_to_mongo()
        connect_to_central()
        start_central()
        update_database()
        update_recognizer()
        main()
    except KeyboardInterrupt:
        shutdown()
