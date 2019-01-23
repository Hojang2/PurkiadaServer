from socket import socket, AF_INET, SOCK_STREAM, gaierror
# from socket import gethostbyname, gethostname
from cryptography.fernet import Fernet, InvalidToken
from json import dumps
from time import clock, sleep
manual = {
        "ls": "  Prints all files and directories in current directory",
        "help": "  Shows this help",
        "ssh": """  Secure Shell - connects you to target server 
                    usage ssh <username>@<target_ip>:<target_port>""",
        "cd": """   Change working directory 
                    usage: cd <target>  parametrs: 
                        cd /            - moves you to root directory
                        cd ..            - moves you to directory above 
                        cd <target_directory>    - moves you to target directory
                    errors:  DirectoryDoesNotExist - target directory doesn't exist""",
        "rename": """ change name of file or directory
            usage: rename <input_file.txt> <output_file.txt>""",
        "su": " Change your user to root",
        "exit": """ If you are connected to server you will be disconnect,
                else close the application""",
        "read": "   Read the content of the file",
        "pwd": "    Prints current working directory"
}

# Creating structures

############################################


class Directory:

    def __init__(self, name: str, permissions: list,
                 upper_directory, owner):
        self.name = name
        self.owner = owner
        self.path = self.name + "/"
        self.type = "directory"
        self.__content = []
        self.permissions = permissions
        if upper_directory:
            self.upper_directory = upper_directory
        else:
            self.upper_directory = self

    def __str__(self) -> str:
        return self.name

    def add(self, new_content) -> None:
        new_content.path = self.path + new_content.path
        self.__content.append(new_content)

    def check_permission(self, permission: str, index: int) -> bool:
        if permission in self.permissions[index]:
            return True
        else:
            return False

    def validate(self, user, permission: str) -> bool:
        if user.name == self.owner:
            return self.check_permission(permission, 0)
        elif user.name == "root":
            return self.check_permission(permission, 0)
        else:
            return self.check_permission(permission, 2)

    def ls(self, user) -> list:
        if self.validate(user, "r"):
            return self.__content
        else:
            return []


class File:

    def __init__(self, name: str, content: str,
                 permissions: str, owner):
        self.type = "file"
        self.name = name
        self.owner = owner
        self.__content = content
        self.permissions = permissions

    def read(self) -> str:
        return self.__content

    def __str__(self) -> str:
        return self.name

##########################
# Client part


class Client:

    def __init__(self, commands, default_directory):
        self.commands = commands
        self.connected = False
        self.port = 0
        self.starter = "{}@{}:{}$"
        self.args = []
        self.action = ""
        self.__password = ""
        self.__sock = None
        self.__key = Fernet.generate_key()
        self.__cipher_suite = Fernet(self.__key)

        # Setting default values
        self.data = False
        self.data_send = None
        self.default_directory = default_directory
        self.cwd = default_directory
        self.path = default_directory.path
        self.default_address = "Kali_linux"
        #  self.default_address = gethostbyname(gethostname())
        self.address = self.default_address
        self.default_name = "guest"
        self.name = self.default_name

    def sock_init(self):

        self.__sock = socket(AF_INET, SOCK_STREAM)
        return True

    def run(self):
        while True:

            self.action = input(self.starter.format(self.name, self.address, self.path))
            self.action, *self.args = self.action.split(" ")

            if self.action in self.commands.keys():
                if self.connected:
                    self.run_connected()
                else:
                    self.run_local()
            else:
                print("Command not found")

    def connect(self):
        if self.sock_init():
            # Syntax of ssh will be 'ssh username@address:port
            tmp = self.args[0].split("@")
            try:
                name = tmp[0]
                tmp = tmp[1]
                address, port = tmp.split(":")
            except IndexError:
                print("Wrong address and port format")
                address, port, name = None, None, None

            try:
                self.__sock.connect((address, int(port)))
                print("new connection with {} on port: {}".format(address, port))
                print(self.__sock.recv(4096).decode("utf-8"))  # Prints banner
                self.validate(name, address, port)

            except gaierror:
                print("Wrong address or port")
            except TypeError:
                print("Wrong input after ssh")
            except ValueError:
                print("Port is not number but String")
            except:
                print("Something goes wrong")

        else:
            print("Problem with socket initialization")

    def validate(self, name, address, port):
        self.__password = input("password: ")
        self.__sock.send(dumps({"name": name, "password": self.__password}).encode())
        self.data = self.__sock.recv(1024).decode("utf-8")
        print(self.data)
        if self.data == "True":
            self.connected = True
            self.path = self.__sock.recv(1024).decode("utf-8")
            sleep(0.1)
            self.__sock.send(self.__key)
            self.name = name
            self.address = address
            self.port = port
        else:
            print("Invalid username or password")
            self.name = self.default_name
        self.run()

    def run_local(self):
        if self.action == "ssh":
            self.connect()

        elif self.action == "exit":
            exit()

        elif self.action == "help":
            self.show_help()

        elif self.action == "cd":
            self.cd()

        elif self.action == "ls":
            tmp = ""
            for obj in self.cwd.ls(self):
                tmp += obj.name + "\n"
            print(tmp)

        elif self.action == "pwd":
            print(self.path)

        if self.action == "read":
            for obj in self.cwd.ls(self):
                if obj.name == self.args:
                    if obj.type == "file":
                        tmp = obj.read()
                    else:
                        tmp = "Target is directory"
                    print(tmp)

    def cd(self):
        if len(self.args) > 0:

            if self.args[0] == "..":

                self.cwd = self.cwd.upper_directory

            elif self.args[0] == "/":

                self.cwd = self.default_directory

            else:
                if len(self.cwd.ls(self)) == 1:
                    self.enter_directory(self.cwd.ls(self)[0])
                else:
                    for obj in self.cwd.ls(self):
                        self.enter_directory(obj)
        else:
            self.cwd = self.default_directory

        self.path = self.cwd.path

    def enter_directory(self, obj):
        if obj.name == self.args[0]:
            if obj.type == "directory":
                self.cwd = obj
            else:
                print("Target is not Directory")

    def show_help(self):
        for key in self.commands:
            print(key + "\t - " + self.commands[key])

    def help_command(self, command):
        print(command + "\t - " + self.commands[command])

    def run_connected(self):
        try:
            if self.action == "help":
                self.show_help()

            elif self.action == "exit":
                self.send_data(dumps({"action": "disconnect", "argv": []}))
                self.receive_data()
                if self.data == "True":
                    self.__sock.close()
                self.disconnect()

            else:
                self.data_send = dumps({"action": self.action, "argv": self.args})
                self.send_data(self.data_send)
                self.receive_data()
                if self.action == "cd":
                    self.path = self.data
                else:
                    print(self.data)
        except ValueError:

            self.disconnect()
            print("Server stop responding disconnected from server")

    def disconnect(self):
        self.__sock.close()
        self.path = self.cwd.path
        self.name = self.default_name
        self.address = self.default_address
        self.connected = False

    def receive_data(self):
        self.data = self.default_directory.path
        try:
            length = int(self.__cipher_suite.decrypt(self.__sock.recv(1024)).decode("utf-8"))
            print("length", length)
            t = clock()
            sleep(0.1)
            self.__sock.send(self.__cipher_suite.encrypt(str(length).encode()))
            self.data = self.__cipher_suite.decrypt(self.__sock.recv(2048)).decode("utf-8")
            print("length", self.data)
            if len(self.data) == length:
                answer = True
            else:
                answer = False
            sleep(0.1)
            self.__sock.send(self.__cipher_suite.encrypt(str(answer).encode()))
            sleep(0.1)
            self.__sock.send(self.__cipher_suite.encrypt(str(clock() - t).encode()))
        except InvalidToken:
            print("Error with receiving data")
            self.disconnect()
        except OSError:
            print("Error with receiving data")
            self.disconnect()

    def send_data(self, data: str) -> bool:
        if len(data) < 1:
            data = "Nothing"
        try:
            length = len(data)
            sleep(0.1)
            self.__sock.send(self.__cipher_suite.encrypt(str(length).encode()))
            temp = int(self.__cipher_suite.decrypt(self.__sock.recv(1024)).decode("utf-8"))
            print("length", temp)
            assert (temp == length), \
                "error with sending length"
            sleep(0.1)
            self.__sock.send(self.__cipher_suite.encrypt(data.encode()))
            temp = self.__cipher_suite.decrypt(self.__sock.recv(1024)).decode("utf-8")
            print("True or False", temp)
            assert (temp == "True"), \
                "Problem with answer from server"
            t = self.__cipher_suite.decrypt(self.__sock.recv(1024)).decode("utf-8")
            print("time", t)
            print("Data transfer complete in {}".format(t))
            return True
        except AssertionError as e:
            print(e)
            return False
        except InvalidToken:
            print("Error with sending data")
            self.disconnect()
        except OSError:
            print("Error with sending data")
            self.disconnect()


main = Directory("", ["rwx", "rwx", "rwx"], None, "root")
d1 = Directory("bin", ["rwx", "rwx", "rwx"], main, "root")
d2 = Directory("home", ["rwx", "rwx", "rwx"], main, "root")
d3 = Directory("guest", ["rwx", "rwx", "rwx"], d2, "root")

d2.add(d3)
main.add(d1)
main.add(d2)
client = Client(manual, main)
client.run()
