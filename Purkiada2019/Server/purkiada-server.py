# -*- coding: utf-8 -*-

import json
import socket
import threading
import structures
import user_class


class Server:

    def __init__(self):

        self.port = 0
        self.address = False
        self.users = []
        self.threads = []
        self.config = False
        self.banner = False
        self.help = False
        self.remote_addresses = []
        self.accept_thread = False

        self.load_config()
        self.get_port()
        self.get_address()
        self.load_banner()
        self.load_help()
        self.sock_init()

    def load_config(self) -> None:

        with open("json/config.json", "r") as f:
            self.config = json.load(f, strict=False)

    def load_banner(self) -> None:

        with open(self.config["banner"], "r") as f:
            self.banner = f.read()

    def get_port(self) -> None:
        self.port = self.config["port"]

    def get_address(self) -> None:
        self.address = self.config["address"]

    def sock_init(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def load_help(self):
        with open(self.config["help"], "r") as f:
            self.help = json.load(f, strict=False)

    def start_server(self):

        self.sock.bind((self.address, self.port))
        self.sock.listen(1)

        self.accept_thread = threading.Thread(target=self.accept_connection)
        self.accept_thread.daemon = False
        self.accept_thread.start()

    def accept_connection(self):

        while True:

            connection, address = self.sock.accept()
            self.remote_addresses.append(address)
            t = threading.Thread(target=self.user_space)
            t.daemon = False
            t.start()
            self.threads.append(t)

    def user_space(self, connection):

        user = user_class.User()
        self.users.append(user)
        user.set_connection(connection)




