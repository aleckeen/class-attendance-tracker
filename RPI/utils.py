import datetime

import data


def info(msg: str):
    print(f"{datetime.datetime.now(tz=data.tz)} [INFO] {msg}")
