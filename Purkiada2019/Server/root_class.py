import user_class


class Root(user_class.User):

    def __init__(self, name, group, default_directory, history_path, history_length, address, server):

        super().__init__(name, group, default_directory, history_path, history_length, address)
        self.server = server
        self.history = user_class.History()

    def set_connection(self, connection):
        super().set_connection(connection)

    def receive_data(self):
        super().receive_data()

    def send_data(self, data: str):
        super().send_data(data)

    def disconnect(self):
        super().disconnect()

    def run_connected(self):
        super().run_connected()

    def log_action(self):
        super().log_action()

    def cd(self):
        super().cd()

    def enter_directory(self, obj):
        super().enter_directory(obj)

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

        temp = ""
        if self.action == "show":
            if self.argv[0] == "users":
                for user in self.server.users:
                    temp += user.name + "\n"
                self.answer = temp
            elif self.argv[0] == "addresses":
                for address in self.server.remote_addresses:
                    temp += address + "\n"
                self.answer = temp
            elif self.argv[0] == "history":

                    for user in self.server.users:
                        if len(self.argv) > 1:
                            if user.name == self.argv[1]:
                                temp += user.history.__str__()
                        else:
                            temp += user.history.__str__()
                    self.answer = temp

        elif self.action == "shutdown":
            self.server.running = False

        elif self.action == "kick":
            for user in self.server.users:
                if user.name == self.argv[0]:
                    user.disconnect()
        elif self.action == "reboot":
            for user in self.server.users:
                user.connected = False
                user.disconnect()
            self.server.sock.close()
            self.server.__init__()

        if self.action == "disconnect":
            self.connected = False
            self.answer = "True"

        if self.action == "submit":
            self.answer = "Done"
