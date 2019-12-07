import tinydb
import json
from typing import List, Optional, Tuple
from enum import Enum

import data
import networking
from utils import info

users = tinydb.TinyDB(data.USERS_PATH)


class Role(Enum):
    Role_Client = "CLIENT"
    Role_Camera = "CAMERA"


class Client(networking.server.Client):
    role: Role
    server: 'Server'
    sock_name: Tuple[str, int]
    selected_cam: Optional['Client'] = None
    location: str
    pi_id: str

    def recv_continuous_client(self):
        while True:
            req = self.recv()
            if req is None:
                break
            elif req == "UNBIND":
                self.selected_cam = None
                info(f"[Server] UNBIND request from {self.sock_name}")
            elif self.selected_cam is not None:
                self.selected_cam.send(req)
                if req == "SCAN":
                    info(f"[Server] SCAN request from {self.sock_name} to {self.selected_cam.sock_name}")
                    while True:
                        res = self.selected_cam.recv()
                        self.send(res)
                        if res == "OK":
                            break
            elif req == "CAMERAS":
                info(f"[Server] CAMERAS request from {self.sock_name}")
                self.server.check_alive(Role.Role_Camera)
                res = {"cameras": []}
                for cam in self.server.get_role(Role.Role_Camera):
                    res['cameras'].append({
                        "location": cam.location,
                        "camera-id": cam.pi_id
                    })
                self.send(json.dumps(res))
            elif req.startswith("BIND"):
                info(f"[Server] BIND request from {self.sock_name}")
                req = req.split("BIND ")[1]
                selected_cam = None
                for cam in self.server.get_role(Role.Role_Camera):
                    if cam.pi_id == req:
                        selected_cam = cam
                        break
                if selected_cam is None:
                    self.send("!")
                else:
                    self.send("OK")
                    self.selected_cam = selected_cam

    def connection_broke(self):
        self.server.clients.remove(self)
        info(f"[Server] Client is no longer alive. address: {self.sock_name}")

    def is_alive(self):
        self.send("ALIVE")
        self.recv()


class Server(networking.server.Server):
    clients: List[Client] = []

    def new_client(self, client: Client) -> bool:
        client.server = self
        client.sock_name = client.tcp_socket.getsockname()
        username = client.recv()
        password = client.recv()
        info(
            f"[Server] A new client attempted to connect: address: {client.sock_name}, username: {username}")
        res = users.search((tinydb.where("username") == username) & (tinydb.where("password") == password))
        if len(res) != 1:
            client.send("!")
            info(f"[Server] Client connection failed. Wrong password or username. "
                 f"address: {client.tcp_socket.getsockname()}")
            return False
        info(f"[Server] Client connection successful. address: {client.sock_name}")
        client.send("OK")
        pos = client.recv()
        if pos == "CAMERA":
            client.role = Role.Role_Camera
            client.pi_id = client.recv()
            client.location = client.recv()
            info(f"[Server] Client added as camera. address: {client.sock_name}")
        elif pos == "CLIENT":
            client.role = Role.Role_Client
            self.executor.submit(client.recv_continuous_client)
            info(f"[Server] Client added. address: {client.sock_name}")
        else:
            client.send("!")
            info(f"[Server] Client connection is refused. Didnt specify role. "
                 f"address: {client.sock_name}")
            return False
        return True

    def get_role(self, role: Role) -> List[Client]:
        clients = []
        for client in self.clients:
            if True if role is None else client.role == role:
                clients.append(client)
        return clients

    def check_alive(self, role: Role):
        info("[Server] Pinging clients.")
        for cam in self.get_role(role):
            cam.is_alive()


def start():
    info("[Server] Starting the server.")
    server = Server(Client)
    info("[Server] Listening for incoming connections.")
    server.listen(data.config["server"]["port"], data.config["server"]["host"])
