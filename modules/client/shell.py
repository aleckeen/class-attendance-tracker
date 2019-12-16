from modules.client import database, data, commands, connection
from modules.client.utils import print_table, show_image

import cmd


class Shell(cmd.Cmd):
    prompt = " >> "
    pre_loop_intro = "Class Attendance Tracker Client\n" \
                     "https://github.com/auriomalley/class-attendance-tracker\n" \
                     "Still in development. May crash frequently.\n" \
                     "^D to exit or simply type: exit"
    doc_header = "A list of available commands. (type: help <command>)"

    def default(self, line):
        if line == "EOF":
            print("Bye")
            return True

    def preloop(self):
        if self.pre_loop_intro:
            self.stdout.write(str(self.pre_loop_intro) + "\n")
        self.onecmd("help")

    def emptyline(self):
        return

    @staticmethod
    def do_exit(arg):
        """Exit the application.
        Usage: exit (Exits the application.)"""
        print("Bye")
        return True

    @staticmethod
    def do_reports(arg):
        """Show reports.
        Usage: reports <date> (Show reports of a given date.)
        Usage: reports <date> <classroom> (Show reports of a given. Filter students by their classrooms.)"""
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
        """Show or add new students.
        Usage: students (Show all students.)
        Usage: students <classroom> (Show all students. Filter students by their classrooms.)
        Usage: students add <camera-id> (Add a new student to the database.)"""
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
        """Download a student's face and view.
        Usage: face <student-id> (Download and view a student's face.)"""
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
        """Show class hours.
        Usage: hours (Show class hours.)"""
        if arg == "set":
            print("Not implemented.")
        elif arg == "":
            hours = data.config["settings"]["hours"]
            table = {"Class": [], "Start": [], "Finish": []}
            for i in range(len(hours)):
                start, finish = hours[i].split()
                table["Class"].append("#" + str(i + 1))
                table["Start"].append(start)
                table["Finish"].append(finish)
            print_table(table)
        else:
            print("Please supply arguments.")

    @staticmethod
    def do_cameras(arg):
        """Show a list of connected cameras.
        Usage: cameras (Show a list of connected cameras.)"""
        cameras = connection.get_cameras()
        table = {"ID": cameras['pi-id'], "Location": cameras["location"]}
        print_table(table)


shell = Shell()
