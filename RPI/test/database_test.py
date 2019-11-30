import json
import os
import time
from io import BytesIO

import vision
import pymongo
import tinydb

MONGO_CONNECTION_PATH = "../data/config/remote_mongo_connection.json"
PROJECT_SETTINGS_PATH = "../data/config/project.json"
STUDENT_FACES_PATH = "../data/student_faces"

with open(PROJECT_SETTINGS_PATH) as f:
    project = json.load(f)

with open(MONGO_CONNECTION_PATH) as f:
    config = json.load(f)
    mongo_remote_url = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}"

STUDENT_FACES_PATH += f"/{project['sub-name']}"
STUDENTS_INFO_PATH = f"{STUDENT_FACES_PATH}/info.json"

if not os.path.isdir(STUDENT_FACES_PATH):
    os.mkdir(STUDENT_FACES_PATH)

remote_db = pymongo.MongoClient(mongo_remote_url).get_database(project['sub-name'])
students_col = remote_db.get_collection("students")
students_info = tinydb.TinyDB(STUDENTS_INFO_PATH)

camera = vision.vision.CameraFeed.create_picamera()


def update():
    ids = []
    for student in students_col.find({}, {"face": 0}):
        inserted_id = str(student['_id'])
        res = students_info.search(tinydb.where('inserted-id') == inserted_id)
        ids.append(inserted_id)
        if len(res) == 1:
            continue
        print(f"Downloading new student info of id {student['id']}")
        face = students_col.find_one({'_id': student['_id']}, {"face": 1})['face']
        face = vision.vision.Frame.open_bytes(face)
        relative_path = f"{inserted_id}.png"
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
            print(f"Removing student with id {student['id']}")
    print("All up to date")


def scan_face() -> vision.vision.Frame:
    while True:
        frame = camera.capture()
        frame.flip(h=True, v=True)
        print("Image has been taken processing please do not move")
        faces = vision.vision.FaceDetector.ageitgey(frame)
        if len(faces) != 1:
            print("Detection failure please do not move")
            continue
        print("You are free to move")
        return faces[0]


def add_new_student():
    student = {'id': input("Student ID> ")}
    if students_col.count_documents({"id": student["id"]}) != 0:
        print(f"A student with id {student['id']} already exists")
        return
    student['name'] = input("Name> ")
    student['classroom'] = input("Classroom> ")
    print("Please get in front of the camera for scanning face")
    input("Press enter when ready")
    time.sleep(2)
    face = scan_face()
    buffer = BytesIO()
    face.write(buffer, ext='.png')
    student['face'] = buffer.getvalue()
    print("Uploading to the central server")
    res = students_col.insert_one(student)
    relative_path = f"{res.inserted_id}.png"
    face.save(f"{STUDENT_FACES_PATH}/{relative_path}")
    students_info.insert({
        'inserted-id': str(res.inserted_id),
        'id': student['id'],
        'name': student['name'],
        'classroom': student['classroom'],
        'face-path': relative_path
    })
    print("New student has been successfully created")
    print(f"\tID={student['id']}")
    print(f"\tName={student['name']}")
    print(f"\tClassroom={student['classroom']}")


def menu():
    print("A - Add new student")
    print("H - Print this helper")
    print("U - Update")
    print("Q - Quit out of the app")


def main():
    menu()
    while True:
        cmd = input("> ")
        if cmd.upper() == 'A':
            add_new_student()
        elif cmd.upper() == 'H':
            menu()
        elif cmd.upper() == 'Q':
            break
        elif cmd.upper() == 'U':
            update()


if __name__ == '__main__':
    try:
        update()
        main()
    except KeyboardInterrupt:
        print("Exiting")
