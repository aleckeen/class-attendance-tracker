from pathlib import Path

import sys
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(Path(os.getcwd()).joinpath("../modules"))

import server

server.start()
