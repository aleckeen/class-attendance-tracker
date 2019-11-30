import datetime
import json

import pandas as pd
import pytz
import pymongo.errors
import networking

MONGO_CONNECTION_PATH = "../data/config/remote_mongo_connection.json"
CENTRAL_CONNECTION_PATH = "../data/config/central_server_connection.json"
PROJECT_SETTINGS_PATH = "../data/config/project.json"

with open(PROJECT_SETTINGS_PATH) as f:
    project = json.load(f)

with open(MONGO_CONNECTION_PATH) as f:
    config = json.load(f)
    mongo_remote_url = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}"

with open(CENTRAL_CONNECTION_PATH) as f:
    config = json.load(f)
    address = (config['host'], config['port'], config['username'], config['password'])

students_col: pymongo.collection.Collection
reports_col: pymongo.collection.Collection

tz = pytz.timezone(project['timezone'])

client: networking.client.Client


def connect_to_mongo() -> bool:
    global students_col
    global reports_col
    try:
        remote_db = pymongo.MongoClient(mongo_remote_url, tz_aware=True)
        remote_db.server_info()
        remote_db = remote_db.get_database(project['sub-name'])
        students_col = remote_db.get_collection("students")
        reports_col = remote_db.get_collection("reports")
        return True
    except pymongo.errors.ServerSelectionTimeoutError:
        return False


def connect_to_central() -> bool:
    global client
    client = networking.client.Client.create()
    status = client.connect(address[0], address[1])
    if status == networking.client.ConnectionStatus.CONNECTION_FAILED:
        return False
    client.send(address[2])
    client.send(address[3])
    res = client.recv()
    if res != "OK":
        return False
    client.send("CLIENT")
    return True


def show_reports():
    location = input("Classroom> ")
    time_start = input("Start time (YYYY-MM-DD HH:MM)> ")
    time_start = datetime.datetime.strptime(time_start, "%Y-%m-%d %H:%M")
    time_start = tz.normalize(tz.localize(time_start)).astimezone(pytz.utc)
    time_end = input("End time (YYYY-MM-DD HH:MM)> ")
    time_end = datetime.datetime.strptime(time_end, "%Y-%m-%d %H:%M")
    time_end = tz.normalize(tz.localize(time_end)).astimezone(pytz.utc)
    table = {
        "ID": [],
        "Name": [],
        "Classroom": [],
        "Count": []
    }
    query = {
        'timestamp': {
            "$gte": time_start,
            "$lt": time_end
        },
        "location": location,
        "student-id": None
    }
    for student in students_col.find({}, {"face": 0}):
        query["student-id"] = student["_id"]
        table["ID"].append(student["id"])
        table["Name"].append(student["name"])
        table["Classroom"].append(student["classroom"])
        table["Count"].append(reports_col.count_documents(query))
    table = pd.DataFrame(data=table)
    table.set_index("ID")
    print(table)


def add_new_student():
    student = {'id': input("Student ID> ")}
    if students_col.count_documents({"id": student["id"]}) != 0:
        print(f"A student with id {student['id']} already exists")
        return
    student['name'] = input("Name> ")
    student['classroom'] = input("Classroom> ")
    client.send("CAMERAS")
    res = client.recv()
    res = json.loads(res)
    for i in range(len(res['cameras'])):
        cam = res['cameras'][i]
        print(f"{i} - {cam['location']}")
    i = int(input("Select a camera for scanning> "))
    client.send(f"BIND {res['cameras'][i]['camera-id']}")
    res = client.recv()
    if res != "OK":
        print("An error occurred during binding")
        return
    print("Please get in front of the camera for face scanning")
    input("Press enter when ready")
    client.send("SCAN")
    client.recv()
    client.send(f"{student['id']}")
    client.send(f"{student['name']}")
    client.send(f"{student['classroom']}")
    client.send("UNBIND")
    print("New student has been successfully created")
    print(f"\tID={student['id']}")
    print(f"\tName={student['name']}")
    print(f"\tClassroom={student['classroom']}")


def menu():
    print("A - Add new student")
    print("R - Show reports")
    print("H - Print this helper")
    print("Q - Quit out of the app")


def main():
    mongo = connect_to_mongo()
    central = connect_to_central()
    if not mongo:
        print("Database connection failed exiting...")
        return
    menu()
    while True:
        cmd = input("> ")
        if cmd.upper() == 'A':
            if not central:
                print("This functionality is unavailable")
                continue
            add_new_student()
        elif cmd.upper() == "R":
            show_reports()
        elif cmd.upper() == 'H':
            menu()
        elif cmd.upper() == 'Q':
            break


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting")
