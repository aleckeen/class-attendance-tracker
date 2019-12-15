import json

from modules import networking
from modules.client import data

address = (data.config['server']['host'], data.config['server']['port'],
           data.config['server']['username'], data.config['server']['password'])

is_connected_server = False

client: networking.Client


def connect_to_server():
    global is_connected_server
    global client
    print("[Client] Attempting to connect to the server.")
    client = networking.Client(networking.create_tcp_socket())
    status = client.connect(address[0], address[1])
    if status == networking.ConnectionStatus.CONNECTION_FAILED:
        is_connected_server = False
        print("[Client] Server connection is failed. Connection failure.")
        return
    client.send(address[2])
    client.send(address[3])
    res = client.recv()
    if res != "OK":
        is_connected_server = False
        print("[Client] Server connection is failed. Unmet credentials.")
        return
    client.send("CLIENT")
    is_connected_server = True
    print("[Client] Server connection is successful.")


def get_cameras():
    client.send("CAMERAS")
    res = client.recv()
    return json.loads(res)


connect_to_server()
