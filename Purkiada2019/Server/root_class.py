import user_class
import structures


class Root(user_class.User):

    def __init__(self, name, group, default_directory, history_path, history_length, server):

        super().__init__(name, group, default_directory, history_path, history_length)
        self.Server = server
        self.history = user_class.History()

    def set_connection(self):
        super().set_connection()

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

        if self.action == "disconnect":
            self.connected = False
            self.answer = "True"

        if self.action == "submit":
            self.answer = "Done"

g = user_class.Group("root")
main = structures.Directory("", ["rwx", "rwx", "rwx"], None, "root", g)
d1 = structures.Directory("home", ["rwx", "rwx", "rwx"], main, "root", g)
d2 = structures.Directory("Documents", ["rwx", "rwx", "rwx"], d1, "root", g)
d3 = structures.Directory("Desktop", ["rwx", "rwx", "rwx"], d1, "root", g)
d4 = structures.Directory(".secret", ["rwx", "rwx", "rwx"], main, "root", g)
d5 = structures.Directory("Downloads", ["rwx", "rwx", "rwx"], d1, "root", g)
d6 = structures.Directory("secret", ["rwx", "rwx", "rwx"], d3, "root", g)
d7 = structures.Directory("pictures", ["rwx", "rwx", "rwx"], d3, "root", g)
d8 = structures.Directory("example", ["rwx", "rwx", "rwx"], d3, "root", g)
d9 = structures.Directory("files", ["rwx", "rwx", "rwx"], d6, "root", g)
d10 = structures.Directory("something", ["rwx", "rwx", "rwx"], d3, "root", g)
main.add(d1)
main.add(d4)
d1.add(d2), d1.add(d3), d1.add(d5), d3.add(d6), d3.add(d7), d3.add(d8), d6.add(d9)
d6.add(d9), d3.add(d10)

root = Root("root", g, main, "users/history/", 20, "sffjs")
print(root.argv)
