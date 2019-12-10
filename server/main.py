from pathlib import Path

import sys
import os

sys.path.append(Path(os.getcwd()).join("../modules"))
os.chdir(os.path.dirname(os.path.realpath(__file__)))

import server

server.start()
