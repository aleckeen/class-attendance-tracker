import pytz

from modules import config as config_manager

CONFIG_PATH = "data/client/config.json"

FOLDERS = [
    "data",
    "data/client"
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

config_manager.create_folders(FOLDERS)
config_manager.create_files(FILES)
config = config_manager.load_config(CONFIG_PATH)
res = config_manager.check_config(config, CONFIG_TEMPLATE)
config_manager.save_config(CONFIG_PATH, config)

if res:
    print(f"Please fill in null values in {CONFIG_PATH}")
    exit(1)

tz = pytz.timezone(config["settings"]['timezone'])
