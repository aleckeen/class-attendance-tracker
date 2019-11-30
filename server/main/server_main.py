import json
import os

from typing import List

import networking
import tinydb

USERS_PATH = "../data/users"
USERS_DATABASE_PATH = f"{USERS_PATH}/db.json"

if not os.path.isdir(USERS_PATH):
    os.makedirs(USERS_PATH)

users = tinydb.TinyDB(USERS_DATABASE_PATH)


class Client(networking.server.Client):
    role: str
    notes = {}

    def recv_continuous_client(self):
        while True:
            req = self.recv()
            if req is None:
                break
            elif req == "UNBIND":
                self.notes['selected'] = None
            elif "selected" in self.notes.keys() and self.notes["selected"] is not None:
                self.notes['selected'].send(req)
                if req == "SCAN":
                    res = self.notes['selected'].recv()
                    self.send(res)
            elif req == "CAMERAS":
                server.check_alive_camera()
                res = {"cameras": []}
                for cam in server.get_role("CAMERA"):
                    res['cameras'].append({
                        "location": cam.notes['location'],
                        "camera-id": cam.notes['pi-id']
                    })
                self.send(json.dumps(res))
            elif req.startswith("BIND"):
                req = req.split("BIND ")[1]
                selected_cam = None
                for cam in server.get_role("CAMERA"):
                    if cam.notes['pi-id'] == req:
                        selected_cam = cam
                        break
                if selected_cam is None:
                    self.send("!")
                else:
                    self.send("OK")
                    self.notes['selected'] = selected_cam

    def connection_broke(self):
        server.clients.remove(self)

    def is_alive(self):
        self.send("ALIVE")
        self.recv()


class Server(networking.server.Server):
    clients: List[Client] = []

    def new_client(self, client: Client) -> bool:
        username = client.recv()
        password = client.recv()
        res = users.search((tinydb.where("username") == username) & (tinydb.where("password") == password))
        if len(res) != 1:
            client.send("!")
            return False
        client.send("OK")
        pos = client.recv()
        client.role = pos
        if pos == "CAMERA":
            client.notes["pi-id"] = client.recv()
            client.notes["location"] = client.recv()
        elif pos == "CLIENT":
            server.executor.submit(client.recv_continuous_client)
        return True

    def get_role(self, role: str) -> List[Client]:
        clients = []
        for client in self.clients:
            if client.role == role:
                clients.append(client)
        return clients

    def check_alive_camera(self):
        for cam in self.get_role("CAMERA"):
            cam.is_alive()


server = Server(Client)
server.listen(5972)
