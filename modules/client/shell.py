from pprint import pprint

import pymongo
from typing import Tuple, Optional

from modules.client import database, data, commands, connection
from modules.client.utils import print_table, show_image

import cmd


def parse(line: str) -> Tuple[Optional[str], Optional[str]]:
    args = line.strip().split()
    if len(args) % 2 == 0:
        return args[-1], None


class Shell(cmd.Cmd):
    prompt = " >> "
    intro = "Class Attendance Tracker Client\n" \
            "https://github.com/auriomalley/class-attendance-tracker"

    def default(self, line):
        if line == "EOF":
            print("Bye")
            return True

    @staticmethod
    def do_exit(arg):
        print("Bye")
        return True

    @staticmethod
    def do_reports(arg):
        args = arg.split()
        if len(args) == 0:
            print("Please supply arguments.")
            return
        location = ''
        if len(args) == 2:
            location = args[1]
        commands.show_reports(args[0], location)

    @staticmethod
    def complete_reports(text, line, begindx, endidx):
        args = line.split(' ')
        completions = []
        if len(args) == 2:
            res = database.reports_col.aggregate([{
                '$project': {'date': {
                    '$dateToString': {'format': '%Y_%m_%d', 'date': "$timestamp",
                                      "timezone": data.config['settings']['timezone']}}}},
                {'$group': {'_id': None, "dates": {'$addToSet': {'date': '$date'}}}}])
            completions = [date['date'] for date in res.next()['dates']]
        elif len(args) == 3:
            completions = database.students_col.distinct("classroom")
        return [completion for completion in completions if completion.startswith(text)]

    @staticmethod
    def do_students(arg):
        if len(arg.split()) == 2 and arg.split()[0] == 'add':
            commands.add_new_student(arg.split()[1])
        else:
            table = {"ID": [], "Name": [], "Classroom": []}
            filters = {'classroom': arg}
            if arg == "":
                filters = {}
            for student in database.students_col.find(filter=filters, projection={"face": False}):
                table["ID"].append(student["id"])
                table["Name"].append(student["name"])
                table["Classroom"].append(student["classroom"])
            print_table(table)

    @staticmethod
    def complete_students(text, line, begindx, endidx):
        if "add" in line:
            cameras = connection.get_cameras()
            completions = cameras["pi-id"]
        else:
            completions: list = database.students_col.distinct("classroom")
            completions.append("add")
        return [completion for completion in completions if completion.startswith(text)]

    @staticmethod
    def do_face(arg):
        student_id = arg
        student = database.students_col.find_one({"id": student_id})
        if student is None:
            print("No matching student is found.")
            return
        show_image(student["face"], f"{student_id} - {student['name']}")

    @staticmethod
    def complete_face(text, line, begindx, endidx):
        completions = database.students_col.distinct('id')
        return [completion for completion in completions if completion.startswith(text)]

    @staticmethod
    def do_hours(arg):
        if arg == "get":
            hours = data.config["settings"]["hours"]
            table = {"Class": [], "Start": [], "Finish": []}
            for i in range(len(hours)):
                start, finish = hours[i].split()
                table["Class"].append("#" + str(i + 1))
                table["Start"].append(start)
                table["Finish"].append(finish)
            print_table(table)
        elif arg == "set":
            print("Not implemented.")
        else:
            print("Please supply arguments.")

    @staticmethod
    def complete_hours(text, line, begindx, endidx):
        completions = ["get", "set"]
        return [completion for completion in completions if completion.startswith(text)]

    @staticmethod
    def do_cameras(arg):
        cameras = connection.get_cameras()
        table = {"ID": cameras['pi-id'], "Location": cameras["location"]}
        print_table(table)


shell = Shell()
