import os

import config as _config
import pytz

os.chdir(os.path.dirname(os.path.realpath(__file__)))

CONFIG_PATH = "data/config.json"
DETECTED_FACES_PATH = "data/detected_faces"
KNOWN_FACES_PATH = "data/known_faces"
KNOWN_FACES_INFO_PATH = f"{KNOWN_FACES_PATH}/info.json"

FOLDERS = [
    "data",
    DETECTED_FACES_PATH,
    KNOWN_FACES_PATH
]

FILES = [
    CONFIG_PATH,
    KNOWN_FACES_INFO_PATH
]

CONFIG_TEMPLATE = {
    "server": {
        "help": "Credentials to connect to the server.",
        "data": {
            "username": {"default": "user", "help": "Username to authenticate."},
            "password": {"default": "password", "help": "Password to authenticate."},
            "host": {"default": "localhost", "help": "IP address of the server."},
            "port": {"default": 5972, "help": "Port where the server is running on."}
        }
    },
    "mongo": {
        "help": "Credentials to connect to the Mongo database.",
        "data": {
            "username": {"help": "Username to authenticate."},
            "password": {"help": "Password to authenticate."},
            "host": {"default": "localhost", "help": "IP address of the server."},
            "port": {"default": 27017, "help": "Port where the server is running on."}
        }
    },
    "settings": {
        "help": "Data to be used by the application internally.",
        "data": {
            "timezone": {"default": "UTC", "help": "Timezone of where you live."},
            "save-images": {"default": False, "help": "Saves every detected face in a folder."}
        }
    },
    "pi": {
        "help": "Information about this Raspberry PI device.",
        "data": {
            "pi-id": {"help": "A distinct ID code, so we know what device we are working on."},
            "location": {"help": "Location of this device."}
        }
    }
}

_config.create_folders(FOLDERS)
_config.create_files(FILES)
config = _config.load_config(CONFIG_PATH)
res = _config.check_config(config, CONFIG_TEMPLATE)
_config.save_config(CONFIG_PATH, config)

if res:
    print(f"Please fill in null values in {CONFIG_PATH}")
    exit(1)

tz = pytz.timezone(config["settings"]['timezone'])
