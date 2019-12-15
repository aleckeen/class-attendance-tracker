import datetime
import pytz

from modules.client import database, connection, data
from modules.client.utils import print_table


def show_cameras():
    res = connection.get_cameras()
    if len(res["pi-id"]) == 0:
        print("No cameras detected.")
    else:
        print_table(res)


def add_new_student(pi_id: str):
    student = {'id': input("Student ID> ")}
    if database.students_col.count_documents({"id": student["id"]}) != 0:
        print(f"A student with id {student['id']} already exists")
        return
    student['name'] = input("Name> ")
    student['classroom'] = input("Classroom> ")
    connection.client.send(f"BIND {pi_id}")
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
    res = input("Do you want to reload the new student information now? [y/N]>")
    if res.upper() == "Y":
        connection.client.send("RELOAD")
    else:
        connection.client.send("!")
    connection.client.send("UNBIND")
    print("New student has been successfully created:")
    print(f"\tID={student['id']}")
    print(f"\tName={student['name']}")
    print(f"\tClassroom={student['classroom']}")


def show_reports(date: str, location: str):
    location = None if location == "" else location
    hours = data.config['settings']['hours']

    table = {
        "ID": [],
        "Name": [],
        "Classroom": []
    }
    for i in range(len(hours)):
        table["#" + str(i + 1)] = []
    filters = {}
    if location is not None:
        filters["classroom"] = location
    for student in database.students_col.find(filters, {"face": False}):
        table["ID"].append(student['id'])
        table["Name"].append(student['name'])
        table["Classroom"].append(student["classroom"])
        for i in range(len(hours)):
            hour = hours[i]
            start, finish = hour.split()
            time_start = datetime.datetime.strptime(f"{date} {start}", "%Y_%m_%d %H:%M")
            time_start = data.tz.normalize(data.tz.localize(time_start)).astimezone(pytz.utc)
            time_finish = datetime.datetime.strptime(f"{date} {finish}", "%Y_%m_%d %H:%M")
            time_finish = data.tz.normalize(data.tz.localize(time_finish)).astimezone(pytz.utc)
            query = {
                'student-id': student['_id'],
                'timestamp': {
                    "$gte": time_start,
                    "$lt": time_finish}}
            count = database.reports_col.count_documents(query)
            table["#" + str(i + 1)].append(count)
    print_table(table)
