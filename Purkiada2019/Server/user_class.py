# -*- coding: utf-8 -*-

import structures
from time import clock


class User:

    def __init__(self, default_directory):
        self.name = None
        self.remote_address = None
        self.default_directory = default_directory
        self.path = default_directory.path
        self.connected = False
        self.__connection = None
        self.data = False
        self.action = None
        self.argv = None
        self.cwd = default_directory
        self.answer = None
        self.permission = "rwx"
        self.root = False

    def cd(self):

        if self.argv[0] == "..":

            self.cwd = self.cwd.upper_directory

        elif self.argv[0] == "/":

            self.cwd = self.default_directory

        else:
            print(len(self.cwd.ls(self.permission)))
            if len(self.cwd.ls(self.permission)) == 1:
                self.enter_directory(self.cwd.ls(self.permission)[0])
            else:
                for obj in self.cwd.ls(self.permission):
                    self.enter_directory(obj)

        self.path = self.cwd.path

    def enter_directory(self, obj):
        if obj.name == self.argv[0]:
            if obj.type == "directory":
                self.cwd = obj
            else:
                print("Target is not Directory")

    def do_action(self):

        self.answer = False

        if self.action == "exit":
            self.answer = "Exiting"
            exit()

        if self.action == "cd":
            self.cd()
            self.answer = self.path

        if self.action == "ls":
            tmp = ""
            for obj in self.cwd.ls(self.permission):
                tmp += obj.name + "\n"
            self.answer = tmp

        if self.action == "pwd":
            self.answer = self.path

        if self.action == "read":
            for obj in self.cwd.ls(self.permission):
                if obj.name == self.argv:
                    if obj.type == "file":
                        self.answer = obj.read()
                    else:
                        print("Target is directory")

    def run(self):
        while True:
            self.action, *self.argv = input(self.path + "$:").split(" ")

            self.do_action()
            print(self.answer)

    def set_connection(self, connection):
        self.__connection = connection

    def receive_data(self):
        length = self.__connection.recv(1024).decode("utf-8")
        t = clock()
        self.__connection.send(length.decode())
        self.data = self.__connection.recv(2048).decode("utf-8")

        if len(self.data) == length:
            answer = True
        else:
            answer = False

        self.__connection.send(str(answer).encode())
        self.__connection.send(str(t - clock()).encode())

    def send_data(self, data: str) -> bool:

        try:
            length = len(self.action)
            self.__connection.send(str(length).encode())
            assert (self.__connection.recv().decode("utf-8") == length), "error with sending length"
            self.__connection.send(data.encode())
            assert (self.__connection.recv().decode("utf-8") == "True"), "Problem with answer from server"
            t = self.__connection.recv().decode("utf-8")
            print("Data transfer complete in {}".format(t))
            return True
        except AssertionError as e:
            print(e)
            return False


folder_names = ["bin", "boot", "dev", "etc", "home", "lib", "mnt", "opt", "root", "sbin", "tmp",
                "usr", "var"]

folder2_names = ["bin", "games", "include", "lib", "local", "sbin", "share", "src"]

main = structures.Directory("", "rwx", None)
folders = [structures.Directory(name, "rwx", main) for name in folder_names]

for folder in folders:
    main.add(folder)


user = User(main)
user.run()
