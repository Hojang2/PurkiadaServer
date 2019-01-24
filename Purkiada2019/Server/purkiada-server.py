# -*- coding: utf-8 -*-

import json
import socket
import threading
import structures
import user_class
import sys
from time import sleep


class Server:

    def __init__(self):

        self.port = 0
        self.address = None
        self.users = []
        self.groups = []
        self.default_group = None
        self.default_directory = None
        self.threads = {}
        self.config = None
        self.banner = None
        self.help = None
        self.__users_list = None
        self.history_path = None
        self.remote_addresses = []
        self.directories = {}
        self.accept_thread = None
        self.sock = None
        self.action = None
        self.args = None

        self.load_config()
        self.get_port()
        self.get_address()
        self.load_banner()
        self.load_users_file()
        self.load_help()
        self.get_history_path()
        self.sock_init()
        self.build_directory_structure()

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

    def get_history_path(self) -> None:
        self.history_path = self.config["history"]

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
        self.accept_thread.daemon = True
        self.accept_thread.start()
        while True:

            self.action, *self.args = input("Server$:").split(" ")
            self.manage_server()

    def manage_server(self):
        if not self.args:
            self.args = ["None"]
        if self.action:
            if self.action == "show":
                if self.args[0] == "users":
                    for user in self.users:
                        print(user.name)
                elif self.args[0] == "addresses":
                    for address in self.remote_addresses:
                        print(address)
                elif self.args[0] == "history":

                        for user in self.users:
                            if len(self.args) > 1:
                                if user.name == self.args[1]:
                                    print(user.history)
                            else:
                                print(user.history)

            elif self.action == "shutdown":
                for user in self.users:
                    user.connected = False
                    user.disconnect()
                self.sock.close()
                sys.exit()
            elif self.action == "kick":
                for user in self.users:
                    if user.name == self.args[0]:
                        user.disconnect()
            elif self.action == "reboot":
                for user in self.users:
                    user.connected = False
                    user.disconnect()
                self.sock.close()
                self.__init__()

    def accept_connection(self):

        while True:
            try:
                connection, address = self.sock.accept()
                address = address[0] + ":" + str(address[1])
                self.remote_addresses.append(address)
                t = threading.Thread(target=self.user_space,
                                     args=(connection, address))
                t.daemon = False
                t.start()

                self.threads[address] = t
            except ValueError as e:
                print(e)
                print("Stop accepting connections")
                sys.exit()

    def user_space(self, connection, address):

        connection.send(self.banner.encode())
        data = json.loads(connection.recv(1024).decode("utf-8"))
        access = False
        for one_user in self.__users_list.values():
            if one_user.get("name") == data.get("name"):
                if one_user["password"] == data["password"]:
                    access = True

        if access:
            if data["name"] == "root":
                pass
            else:
                user = user_class.User(data["name"],
                                       self.default_group, self.default_directory,
                                       self.history_path, self.config["history_length"])

                if data["name"] in self.directories:
                    user.cwd = self.directories[data["name"]]
                    user.path = user.cwd.path

                self.users.append(user)
                user.set_connection(connection)
                connection.send("True".encode())
                sleep(0.1)
                connection.send(user.path.encode())
                user.run_connected()
                user.disconnect()
                self.directories[user.name] = user.cwd
                self.users.remove(user)
                self.remote_addresses.remove(address)
                sys.exit()

        else:
            connection.send("False".encode())
            self.remote_addresses.remove(address)

    def build_directory_structure(self):

        g = user_class.Group("root")
        self.groups.append(g)

        main = structures.Directory("", ["rwx", "rwx", "rwx"], None, "root", g)
        d1 = structures.Directory("bin", ["rwx", "rwx", "rwx"], main, "root", g)
        d2 = structures.Directory(".home", ["rwx", "rwx", "rwx"], main, "root", g)
        d3 = structures.Directory("guest", ["rwx", "rwx", "rwx"], d2, "root", g)
        d4 = structures.Directory("media", ["rwx", "rwx", "rwx"], main, "root", g)
        d5 = structures.Directory("dev", ["rwx", "rwx", "rwx"], main, "root", g)
        d6 = structures.Directory("log", ["rwx", "rwx", "rwx"], d5, "root", g)
        d7 = structures.Directory("rtc", ["rwx", "rwx", "rwx"], d5, "root", g)
        d8 = structures.Directory("net", ["rwx", "rwx", "rwx"], d5, "root", g)
        d9 = structures.Directory("cdrom", ["rwx", "rwx", "rwx"], main, "root", g)
        d10 = structures.Directory(".var", ["rwx", "rwx", "rwx"], main, "root", g)
        d11 = structures.Directory(".backups", ["rwx", "rwx", "rwx"], d10, "root", g)
        d12 = structures.Directory(".local", ["rwx", "rwx", "rwx"], d10, "root", g)
        d13 = structures.Directory("log", ["rwx", "rwx", "rwx"], d10, "root", g)
        d14 = structures.Directory("run", ["rwx", "rwx", "rwx"], d10, "root", g)
        d15 = structures.Directory("network", ["rwx", "rwx", "rwx"], d14, "root", g)
        d16 = structures.Directory("mount", ["rwx", "rwx", "rwx"], d14, "root", g)
        d17 = structures.Directory("deleted_files", ["rwx", "rwx", "rwx"], d11, "root", g)

        f0 = structures.File("File1", "Content of file", ["rwx", "rwx", "rwx"], "root", g)
        f1 = structures.File("secret.txt", "Here is secret password", ["rwx", "rwx", "rwx"], "root", g)
        f2 = structures.File("cd.iso", "unable to open iso file", ["rwx", "rwx", "rwx"], "root", g)
        f3 = structures.File("log.log", "Wed Jan 23 13:43:56 2019 /$:disconnect []", ["rwx", "rwx", "rwx"], "root", g)

        d2.add(f0), d9.add(f2), d13.add(f3), d17.add(f1)
        d2.add(d3), main.add(d1), main.add(d2), main.add(d4), main.add(d5)
        d5.add(d6), d5.add(d7), d5.add(d8), main.add(d9), main.add(d10)
        d10.add(d11), d10.add(d12), d10.add(d13), d10.add(d14), d14.add(d15)
        d14.add(d16), d11.add(d17)

        self.default_group = user_class.Group("users_group")
        self.default_directory = main

        self.groups.append(self.default_group)


server = Server()
server.start_server()
