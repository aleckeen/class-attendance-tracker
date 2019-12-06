import concurrent.futures.thread

import socket
from enum import Enum, auto
from typing import Tuple, List, Optional, Callable


def send(tcp_socket: socket.socket, data: str, encoding: str = "UTF-8", header_len: int = 16):
    data_len = str(len(data)).zfill(header_len)
    data = f"{data_len}{data}"
    tcp_socket.sendall(data.encode(encoding=encoding))


def recv(tcp_socket: socket.socket, encoding: str = "UTF-8", header_len: int = 16) -> Optional[str]:
    header = tcp_socket.recv(header_len)
    if not header:
        return None
    header = header.decode(encoding=encoding)
    data_len = int(header)
    data = tcp_socket.recv(data_len)
    if not data:
        return None
    data = data.decode(encoding=encoding)
    return data


def create_tcp_socket() -> socket.socket:
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class ConnectionStatus(Enum):
    CONNECTION_SUCCESSFUL = auto()
    ALREADY_CONNECTED = auto()
    CONNECTION_FAILED = auto()


class DisconnectionStatus(Enum):
    NOT_CONNECTED = auto()
    DISCONNECTION_SUCCESSFUL = auto()


class Client:
    tcp_socket: socket.socket
    address: Tuple[str, int] = ('', 0)

    is_connected: bool = False

    def __init__(self, tcp_socket: socket.socket):
        self.tcp_socket = tcp_socket

    def __del__(self):
        self.disconnect()

    def connect(self, host: str, port: int) -> ConnectionStatus:
        if self.is_connected:
            return ConnectionStatus.ALREADY_CONNECTED
        try:
            self.tcp_socket.connect((host, port))
            self.address = (host, port)
            self.is_connected = True
            return ConnectionStatus.CONNECTION_SUCCESSFUL
        except ConnectionError:
            return ConnectionStatus.CONNECTION_FAILED

    def disconnect(self) -> DisconnectionStatus:
        if not self.is_connected:
            return DisconnectionStatus.NOT_CONNECTED
        self.tcp_socket.shutdown(socket.SHUT_RDWR)
        self.tcp_socket.close()
        self.address = ('', 0)
        self.is_connected = False
        return DisconnectionStatus.DISCONNECTION_SUCCESSFUL

    def send(self, data: str):
        send(self.tcp_socket, data)

    def recv(self) -> str:
        data = recv(self.tcp_socket)
        if data is None:
            self.disconnect()
            self.connection_broke()
        return data

    def connection_broke(self):
        pass


class Server:
    tcp_socket: socket.socket
    executor = concurrent.futures.thread.ThreadPoolExecutor()
    client_class: Callable[[socket.socket], Client]

    clients: List[Client] = []

    def __init__(self, client_class: Callable[[socket.socket], Client]):
        self.tcp_socket = create_tcp_socket()
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_class = client_class

    def __del__(self):
        for client in self.clients:
            client.disconnect()
        self.tcp_socket.shutdown(socket.SHUT_RDWR)
        self.tcp_socket.close()
        self.executor.shutdown()

    def listen(self, port: int, host=''):
        self.tcp_socket.bind((host, port))
        self.tcp_socket.listen()
        while True:
            connection, address = self.tcp_socket.accept()
            client = self.client_class(connection)
            status = self.new_client(client)
            if status:
                self.clients.append(client)

    def new_client(self, client: Client) -> bool:
        return True
