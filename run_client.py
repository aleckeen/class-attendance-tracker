import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from modules.client import shell, database


def main():
    if not database.is_connected_mongo:
        print("Database is unavailable. Will exit.")
        exit(1)
    shell.shell.cmdloop()


if __name__ == '__main__':
    main()
