from pathlib import Path

import sys
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(str(Path(os.getcwd()).parents[0].joinpath("modules")))

import server

server.start()
