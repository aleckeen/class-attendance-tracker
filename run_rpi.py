import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from modules.rpi import camera
from modules.rpi import connection
from modules.rpi import database
from modules.utils import info

detector = camera.StudentDetector()


def shutdown():
    info("[RPi] Exiting.")
    detector.report()


def main():
    database.sync_database()
    camera.update_recognizer()
    connection.connect_to_server()
    connection.recv_from_server()
    detector.start()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        shutdown()
