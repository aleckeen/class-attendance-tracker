import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from enum import Enum, auto

from modules.rpi import camera
from modules.rpi import connection
from modules.rpi import database
from modules.utils import info


class Job(Enum):
    DETECT_STUDENTS = auto()
    REPORT = auto()
    SHUTDOWN = auto()


CURRENT_JOB = Job.DETECT_STUDENTS


def shutdown():
    info("[rpi] Exiting")
    camera.report()


def main():
    global CURRENT_JOB
    while True:
        if len(camera.reports) > 10 and database.is_connected_mongo and CURRENT_JOB != Job.REPORT:
            CURRENT_JOB = Job.REPORT
        elif CURRENT_JOB == Job.DETECT_STUDENTS:
            camera.detect_students()
        elif CURRENT_JOB == Job.REPORT:
            camera.report()
            if CURRENT_JOB == Job.REPORT:
                CURRENT_JOB = Job.DETECT_STUDENTS
        elif CURRENT_JOB == Job.SHUTDOWN:
            shutdown()
            break


if __name__ == '__main__':
    try:
        database.connect_to_mongo()
        database.sync_database()
        camera.update_recognizer()
        connection.connect_to_server()
        connection.recv_from_server()
        main()
    except KeyboardInterrupt:
        shutdown()
