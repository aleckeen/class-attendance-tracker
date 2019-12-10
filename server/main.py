from pathlib import Path

import sys
import os

sys.path.append(Path(os.getcwd()).joinpath("../modules"))
os.chdir(os.path.dirname(os.path.realpath(__file__)))

import server

server.start()
