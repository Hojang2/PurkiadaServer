# -*- coding: utf-8 -*-

import structures


class User:

    def __init__(self, default_directory):
        self.name = None
        self.remote_address = None
        self.default_directory = default_directory
        self.path = default_directory.path
        self.connected = False
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


folder_names = ["bin", "boot", "dev", "etc", "home", "lib", "mnt", "opt", "root", "sbin", "tmp",
                "usr", "var"]

folder2_names = ["bin", "games", "include", "lib", "local", "sbin", "share", "src"]

main = structures.Directory("", "rwx", None)
folders = [structures.Directory(name, "rwx", main) for name in folder_names]

for folder in folders:
    main.add(folder)


user = User(main)
user.run()
