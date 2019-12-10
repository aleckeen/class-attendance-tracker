import tinydb
import utils
import config as _config
import pytz

CONFIG_PATH = "data/config.json"
LOG_PATH = "data/log.json"
USERS_PATH = "data/users.json"

FOLDERS = [
    "data"
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

_config.create_folders(FOLDERS)
_config.create_files(FILES)
config = _config.load_config(CONFIG_PATH)
res = _config.check_config(config, CONFIG_TEMPLATE)
_config.save_config(CONFIG_PATH, config)

if res:
    print(f"Please fill in null values in {CONFIG_PATH}")
    exit(1)

log_db = tinydb.TinyDB(LOG_PATH)
tz = pytz.timezone(config["settings"]['timezone'])
utils.tz = tz
utils.log_db = log_db
