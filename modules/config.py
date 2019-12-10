import json
from pathlib import Path
from typing import Dict, Any, List


def create_folders(folders: List[str]):
    for folder in folders:
        path = Path(folder)
        if not path.is_dir():
            path.mkdir()


def create_files(files: List[str]):
    for file in files:
        path = Path(file)
        if not path.is_file():
            path.touch()


def load_config(path: str) -> Dict[str, Any]:
    with open(Path(path), "rb") as f:
        try:
            config = json.load(f)
        except ValueError:
            config = {}
    return config


def save_config(path: str, config: Dict[str, Any]):
    with open(Path(path), "w") as f:
        json.dump(config, f, indent=2)


def check_config(config: Dict[str, Any], template: Dict[str, Any]) -> bool:
    found_none = False
    for key in template.keys():
        if key not in config.keys():
            config[key] = None

        if config[key] is None:
            if "default" in template[key].keys():
                config[key] = template[key]["default"]

            elif "data" in template[key].keys():
                config[key] = {}

        if "data" in template[key].keys():
            res = check_config(config[key], template[key]["data"])
            found_none = found_none or res

        found_none = found_none or config[key] is None

    return found_none
