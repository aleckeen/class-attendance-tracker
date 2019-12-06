import networking
import threading

import camera
import data
from utils import info

address = (data.config['server']['host'], data.config['server']['port'],
           data.config['server']['username'], data.config['server']['password'])

is_connected_server = False


class Client(networking.client.Client):
    def connection_broke(self):
        global is_connected_server
        info("[Client] Connection broken.")
        is_connected_server = False

    def respond_to_server(self):
        while True:
            req = self.recv()
            if req is None:
                break
            elif req == "SCAN":
                camera.scan_face()
            elif req == "ALIVE":
                self.send("OK")


client = Client(networking.create_tcp_socket())


def connect_to_server():
    global is_connected_server
    global client
    info("[Client] Attempting to connect to the server.")
    client = Client(networking.create_tcp_socket())
    status = client.connect(address[0], address[1])
    if status == networking.client.ConnectionStatus.CONNECTION_FAILED:
        is_connected_server = False
        info("[Client] Server connection is failed. Connection failure.")
        return
    client.send(address[2])
    client.send(address[3])
    res = client.recv()
    if res != "OK":
        is_connected_server = False
        info("[Client] Server connection is failed. Unmet credentials.")
        return
    client.send("CAMERA")
    client.send(data.config['pi']['pi-id'])
    client.send(data.config['pi']['location'])
    is_connected_server = True
    info("[Client] Server connection is successful.")


def recv_from_server():
    if is_connected_server:
        t = threading.Thread(target=client.respond_to_server)
        t.daemon = True
        t.start()
