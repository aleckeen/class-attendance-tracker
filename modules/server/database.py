from modules.server import data

import tinydb

users = tinydb.TinyDB(data.USERS_PATH, indent=2)

if len(users.all()) == 0:
    print("No user found. Please add at least one user.")
    res = input("Would you like to create a user? [y/N]> ")
    if res.upper() == "Y":
        username = input("Username> ")
        password = input("Password> ")
        users.insert({"username": username, "password": password})
    else:
        print("Exiting. Please add user.")
        exit(1)
