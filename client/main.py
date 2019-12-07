import connection
import data
import database

import datetime
import json
import pandas as pd
import pytz


def show_reports():
    location = input("Classroom> ")
    location = None if location == "" else location
    try:
        time_start = input("Start time (YYYY-MM-DD HH:MM)> ")
        time_start = None if time_start == "" else time_start
        time_end = input("End time (YYYY-MM-DD HH:MM)> ")
        time_end = None if time_end == "" else time_end

        if time_start is not None:
            time_start = datetime.datetime.strptime(time_start, "%Y-%m-%d %H:%M")
            time_start = data.tz.normalize(data.tz.localize(time_start)).astimezone(pytz.utc)

        if time_end is not None:
            time_end = datetime.datetime.strptime(time_end, "%Y-%m-%d %H:%M")
            time_end = data.tz.normalize(data.tz.localize(time_end)).astimezone(pytz.utc)
    except ValueError:
        print("Cancelling.")
        return
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

    if time_start is None:
        del query["timestamp"]["$gte"]
    if time_end is None:
        del query["timestamp"]["$lt"]
    if time_start is None and time_end is None:
        del query["timestamp"]
    if location is None:
        del query["location"]

    for student in database.students_col.find({}, {"face": 0}):
        query["student-id"] = student["_id"]
        table["ID"].append(student["id"])
        table["Name"].append(student["name"])
        table["Classroom"].append(student["classroom"])
        table["Count"].append(database.reports_col.count_documents(query))
    table = pd.DataFrame(data=table)
    table.set_index("ID")
    print(table)


def add_new_student():
    student = {'id': input("Student ID> ")}
    if database.students_col.count_documents({"id": student["id"]}) != 0:
        print(f"A student with id {student['id']} already exists")
        return
    student['name'] = input("Name> ")
    student['classroom'] = input("Classroom> ")
    connection.client.send("CAMERAS")
    res = connection.client.recv()
    res = json.loads(res)
    if len(res["cameras"]) == 0:
        print("No camera is detected.")
        return
    for i in range(len(res['cameras'])):
        cam = res['cameras'][i]
        print(f"{i} - {cam['location']}")
    i = int(input("Select a camera for scanning> "))
    connection.client.send(f"BIND {res['cameras'][i]['camera-id']}")
    res = connection.client.recv()
    if res != "OK":
        print("An error occurred during binding")
        return
    print("Please get in front of the camera for face scanning")
    input("Press enter when ready")
    connection.client.send("SCAN")
    while True:
        res = connection.client.recv()
        if res == "OK":
            break
        print("A detection failure occurred. Please do not move.")
    connection.client.send(f"{student['id']}")
    connection.client.send(f"{student['name']}")
    connection.client.send(f"{student['classroom']}")
    connection.client.send("UNBIND")
    print("New student has been successfully created:")
    print(f"\tID={student['id']}")
    print(f"\tName={student['name']}")
    print(f"\tClassroom={student['classroom']}")


def menu():
    print("A - Add new student")
    print("R - Show reports")
    print("H - Print this helper")
    print("Q - Quit out of the app")


def main():
    if not database.is_connected_mongo:
        print("Database is unavailable. Will exit.")
        exit(1)
    menu()
    while True:
        cmd = input("> ")
        if cmd.upper() == 'A':
            if not connection.is_connected_server:
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
