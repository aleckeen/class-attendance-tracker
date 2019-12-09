import os
import pytz

import config as _config

os.chdir(os.path.dirname(os.path.realpath(__file__)))

CONFIG_PATH = "data/config.json"

FOLDERS = [
    "data"
]

FILES = [
    CONFIG_PATH,
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
            "timezone": {"default": "UTC", "help": "Timezone of where you live."}
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
