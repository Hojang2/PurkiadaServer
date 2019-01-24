# -*- coding: utf-8 -*-

from time import clock, sleep, ctime
import json


class Group:

    def __init__(self, name):
        self.name = name
        self.__users = []

    def add(self, u):
        self.__users.append(u)

    def remove(self, u):
        self.__users.remove(u)

    def list(self):
        return self.__users


class User:

    def __init__(self, name, group, default_directory, history_path, history_length):
        self.name = name
        self.group = group
        self.group.add(self)
        self.log_file = history_path + self.name + "_log.Log"
        self.history = History(history_length)
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

    def cd(self):
        if len(self.argv) > 0:
            if self.argv[0] == "..":

                self.cwd = self.cwd.upper_directory

            elif self.argv[0] == "/":

                self.cwd = self.default_directory

            else:
                if len(self.cwd.ls(self)) == 1:
                    self.enter_directory(self.cwd.ls(self)[0])
                else:
                    for obj in self.cwd.ls(self):
                        self.enter_directory(obj)
        else:
            self.cwd = self.default_directory

        print(self.cwd)
        self.path = self.cwd.path

    def enter_directory(self, obj):
        if obj.name == self.argv[0]:
            if obj.type == "directory":
                self.cwd = obj
            else:
                print("Target is not Directory")

    def log_action(self):
        self.history.add(self.action, self.argv, self.path)
        with open(self.log_file, "a") as f:
            f.write("{} {}$:{} {}\n".format(ctime(), self.path, self.action, self.argv))

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
            if len(self.argv) == 0:
                self.argv = ["None"]

            if "a" in self.argv[0]:
                visible_list = self.cwd.ls(self)
            else:
                visible_list = []
                for obj in self.cwd.ls(self):
                    if obj.name[0] != ".":
                        visible_list.append(obj)

            for obj in visible_list:
                if "l" in self.argv[0]:
                    line = " {} {}:{}:{} {} {} {}\n".format(obj.type, obj.permissions[0],
                                                            obj.permissions[1], obj.permissions[2],
                                                            obj.owner, obj.group.name, obj.name)
                else:
                    line = obj.name + "\n"
                tmp += line

            self.answer = tmp

        if self.action == "pwd":
            self.answer = self.path

        if self.action == "read":
            if len(self.argv) == 0:
                self.argv = ["None"]
            else:
                self.argv = self.argv[0]

            for obj in self.cwd.ls(self):
                if obj.name == self.argv:
                    if obj.type == "file":
                        self.answer = obj.read()
                    else:
                        self.answer = "Target is directory"

        if self.action == "disconnect":
            self.connected = False
            self.answer = "True"

        if self.action == "submit":
            self.answer = "Done"

    def run_connected(self):
        self.connected = True
        while self.connected:
            try:
                self.receive_data()
                self.data = json.loads(self.data)

                self.action, self.argv = self.data["action"], self.data["argv"]
                self.log_action()

                self.do_action()
                sleep(0.1)
                self.send_data(self.answer)
            except OSError:
                print("disconnecting user {} from server".format(self.name))
                break
            except TypeError:
                print("disconnecting user {} from server".format(self.name))
                break
            except:
                print("Some not handled error")
                break

    def run(self):
        while True:
            self.action, *self.argv = input(self.path + "$:").split(" ")

            self.do_action()
            print(self.answer)

    def set_connection(self, connection):
        self.__connection = connection

    def receive_data(self):
        self.data = self.default_directory.path
        try:
            length = int(self.__connection.recv(1024).decode("utf-8"))
            print("length", length)
            t = clock()
            sleep(0.1)
            self.__connection.send(str(length).encode())
            self.data = self.__connection.recv(2048).decode("utf-8")
            print("length", self.data)
            if len(self.data) == length:
                answer = True
            else:
                answer = False
            sleep(0.1)
            self.__connection.send(str(answer).encode())
            sleep(0.1)
            self.__connection.send(str(clock() - t).encode())
        except OSError:
            print("Error with receiving data")
            self.disconnect()

    def send_data(self, data: str) -> bool:
        if len(data) < 1:
            data = "Nothing"
        try:
            length = len(data)
            sleep(0.1)
            self.__connection.send(str(length).encode())
            temp = int(self.__connection.recv(1024).decode("utf-8"))
            # print("length", temp)
            assert (temp == length), \
                "error with sending length"
            sleep(0.1)
            self.__connection.send(data.encode())
            temp = self.__connection.recv(1024).decode("utf-8")
            # print("True or False", temp)
            assert (temp == "True"), \
                "Problem with answer from server"
            t = self.__connection.recv(1024).decode("utf-8")
            # print("Data transfer complete in {}".format(t))
            return True
        except AssertionError as e:
            print(e)
            return False
        except OSError:
            print("Error with sending data")
            self.disconnect()

    def disconnect(self):
        self.__connection.close()


class History:
    def __init__(self, length=10):
        self.__history = []
        self.__length = length

    def add(self, action, argv, path):
        tmp = ""
        for index in argv:
            tmp += index + " "
        if len(self.__history) == self.__length:
            del self.__history[0]
        self.__history.append("{} {}$:{} {}\n".format(ctime(), path, action, argv))

    def clear(self):
        self.__history = []

    def __str__(self):
        tmp = ""
        for line in self.__history:
            tmp += line
        return tmp
