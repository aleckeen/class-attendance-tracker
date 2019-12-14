import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from modules.server import server

server.start()
