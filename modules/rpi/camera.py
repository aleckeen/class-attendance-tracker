import os

import bson
import datetime
import io
import pymongo
import threading

from typing import List, Dict, Any

from modules.rpi import connection
from modules.rpi import data
from modules.rpi import database
from modules.database import get_mongo_client
from modules.rpi import vision
from modules.utils import info

camera = vision.CameraFeed.create_picamera()
recognizer: vision.FaceRecognizer
reports: List[Dict[str, Any]] = []
current_frame: vision.Frame = camera.capture()


def continuous_capture():
    global current_frame
    while True:
        frame = camera.capture()
        frame.flip(h=True, v=True)
        current_frame = frame


def update_recognizer():
    global recognizer
    info("[Recognizer] Updating the recognizer instance.")
    faces: List[vision.Frame] = []
    ids: List[str] = []
    for student in database.students_info.all():
        frame = vision.Frame.open_path(f"{data.KNOWN_FACES_PATH}/{student['face-path']}")
        faces.append(frame)
        ids.append(student['inserted-id'])
    recognizer = vision.FaceRecognizer(zip(faces, ids))
    info("[Recognizer] Recognizer update finished.")


def scan_face():
    info("[Scanner] Scanning.")
    success, db = get_mongo_client(database.mongo_remote_url)
    students_col = db.get_collection("students")
    while True:
        frame = current_frame.copy()
        faces = vision.FaceDetector.opencv(frame)
        if len(faces) == 0:
            connection.client.send("!")
            continue
        faces = vision.FaceDetector.ageitgey(frame)
        if len(faces) != 1:
            info("[Scanner] Detection failure.")
            connection.client.send("!")
            continue
        info("[Scanner] Successfully scanned a face.")
        connection.client.send("OK")
        break
    student_id = connection.client.recv()
    student_name = connection.client.recv()
    classroom = connection.client.recv()
    reload = connection.client.recv() == "RELOAD"
    face_bin = io.BytesIO()
    faces[0].write(face_bin, ".jpg")
    student = {
        "id": student_id,
        "name": student_name,
        "classroom": classroom,
        "face": face_bin.getvalue()
    }
    students_col.insert_one(student)
    if reload:
        database.sync_database()
        update_recognizer()


class StudentDetector:
    reports = []
    reports_col: pymongo.collection.Collection
    is_connected = False
    work = True  # Can be useful in the future.
    is_connecting = False

    def __init__(self):
        self.connect_to_db()

    def connect_to_db(self):
        info("[Detector] Attempting to connect to the database.")
        self.is_connecting = True
        success, db = get_mongo_client(database.mongo_remote_url)
        if success:
            info("[Detector] Database connection is successful.")
            self.reports_col = db.get_collection("reports")
            self.is_connected = True
        else:
            info("[Detector] Database connection failed.")
            self.is_connected = False
        self.is_connecting = False

    def detect_students(self):
        frame = current_frame.copy()
        faces = vision.FaceDetector.opencv(frame)
        if len(faces) > 0:
            info(f"[Detector] Found {len(faces)} face(s).")
        for student_id, face in recognizer.recognize_threaded(faces):
            if student_id == -1:
                student_id = "unknown"
            elif student_id is None:
                student_id = "recognition-failure"
            else:
                student_id = bson.ObjectId(student_id)
            timestamp = datetime.datetime.now(tz=data.tz)
            self.reports.append({
                "pi-id": data.config["pi"]["pi-id"],
                "location": data.config["pi"]["location"],
                "student-id": student_id,
                "timestamp": timestamp
            })
            info(f"[Detector] Detected a student with database-id {student_id}.")
            if data.config["settings"]["save-images"]:
                path = f"{data.DETECTED_FACES_PATH}/{student_id}"
                if not os.path.isdir(path):
                    os.mkdir(path)
                face.save(f"{path}/{timestamp}.jpg")

    def start(self):
        while self.work:
            self.detect_students()
            self.report()

    def report(self):
        if len(self.reports) > 10:
            if self.is_connected:
                info("[Reporter] Reporting.")
                self.reports_col.insert_many(self.reports)
                self.reports = []
            else:
                if not self.is_connecting:
                    db_t = threading.Thread(target=self.connect_to_db)
                    db_t.daemon = True
                    db_t.start()


recorder_t = threading.Thread(target=continuous_capture)
recorder_t.daemon = True
recorder_t.start()
