import sys
import tinydb
import pytz

from modules import utils
from modules import config as config_manager

CONFIG_PATH = "data/server/config.json"
LOG_PATH = "data/server/log.json"
USERS_PATH = "data/server/users.json"

FOLDERS = [
    "data",
    "data/server"
]

FILES = [
    CONFIG_PATH,
    USERS_PATH,
    LOG_PATH
]

CONFIG_TEMPLATE = {
    "server": {
        "help": "Credentials to connect to the server.",
        "data": {
            "host": {"default": "", "help": "IP address that you want to bind the server to."},
            "port": {"default": 5972, "help": "Port where you want to bind the server to."}
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
    sys.exit(1)

log_db = tinydb.TinyDB(LOG_PATH)
tz = pytz.timezone(config["settings"]['timezone'])
utils.tz = tz
utils.log_db = log_db
