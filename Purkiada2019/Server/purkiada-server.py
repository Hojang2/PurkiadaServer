# -*- coding: utf-8 -*-

import json
import socket
import threading
import structures
import user_class


class Server:

    def __init__(self):

        self.port = 0
        self.address = None
        self.users = []
        self.groups = []
        self.default_group = None
        self.default_directory = None
        self.threads = []
        self.config = None
        self.banner = None
        self.help = None
        self.__users_list = None
        self.remote_addresses = []
        self.accept_thread = None
        self.sock = None

        self.load_config()
        self.get_port()
        self.get_address()
        self.load_banner()
        self.load_users_file()
        self.load_help()
        self.sock_init()
        self.test_Directory()

    def load_config(self) -> None:

        with open("json/config.json", "r") as f:
            self.config = json.load(f, strict=False)

    def load_banner(self) -> None:

        with open(self.config["banner"], "r") as f:
            self.banner = f.read()

    def load_users_file(self)-> None:
        with open(self.config["user_file"], "r") as f:
            self.__users_list = json.load(f, strict=False)

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
        print(self.address, self.port)
        self.sock.bind((self.address, self.port))
        self.sock.listen(1)

        self.accept_thread = threading.Thread(target=self.accept_connection)
        self.accept_thread.daemon = False
        self.accept_thread.start()

    def accept_connection(self):

        while True:

            connection, address = self.sock.accept()

            self.remote_addresses.append(address)
            t = threading.Thread(target=self.user_space, args=(connection, address))
            t.daemon = False
            t.start()
            self.threads.append(t)

    def user_space(self, connection, address):

        connection.send(self.banner.encode())
        data = json.loads(connection.recv(1024).decode("utf-8"))
        access = False
        for one_user in self.__users_list.values():
            if one_user.get("name") == data.get("name"):
                if one_user["password"] == data["password"]:
                    access = True

        if access:
            user = user_class.User(data["name"], self.default_group, self.default_directory)
            self.users.append(user)
            user.set_connection(connection)
            connection.send("True".encode())
            connection.send(user.path.encode())
            user.run_connected()

        else:
            connection.send("False".encode())
            self.remote_addresses.remove(address)

    def test_Directory(self):
        folder_names = ["bin", "boot", "dev", "etc", "home", "lib", "mnt", "opt", "root", "sbin", "tmp",
                        "usr", "var"]

        folder2_names = ["bin", "games", "include", "lib", "local", "sbin", "share", "src"]

        g = user_class.Group("root")
        self.groups.append(g)
        main = structures.Directory("", ["rwx", "rwx", "rwx"], None, "root", g)
        folders = [structures.Directory(name, ["rwx", "rwx", "rwx"], main, "root", g) for name in folder_names]

        for folder in folders:
            main.add(folder)

        self.default_group = user_class.Group("users_group")
        self.default_directory = main

        self.groups.append(self.default_group)


server = Server()
server.start_server()

