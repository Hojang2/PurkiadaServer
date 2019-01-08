from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
from json import dumps
from time import clock
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


class Client:

    def __init__(self, commands):
        self.commands = commands
        self.connected = False
        self.port = 0
        self.starter = "{}@{}:{}$"
        self.args = []
        self.action = ""
        self.__password = ""
        self.__sock = None

        # Setting default values
        self.data = False
        self.data_send = None
        self.default_path = "/home/guest"
        self.path = self.default_path
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
            self.name = tmp[0]
            tmp = tmp[1]
            self.address, self.port = tmp.split(":")

            print(self.address, self.port)
            self.__sock.connect((self.address, int(self.port)))
            self.connected = True
            print("new connection with {} on port: {}".format(self.address,
                                                              self.port))
            print(self.__sock.recv(4096).decode("utf-8"))  # Prints banner
            self.validate()

        else:
            print("Problem with socket initialization")

    def validate(self):
        self.__password = input("password: ")
        self.__sock.send(dumps({"name": self.name, "password": self.__password}).encode())
        self.data = self.__sock.recv(1024).decode("utf-8")
        if self.data == "True":
            self.connected = True
            self.path = self.__sock.recv(1024).decode("utf-8")
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
                self.path = self.default_path
                self.name = self.default_name
                self.address = self.default_address
                self.connected = False

            else:
                self.data_send = dumps({"action": self.action, "argv": self.args})
                self.send_data(self.data_send)
                self.receive_data()
                if self.action == "cd":
                    self.path = self.data
                else:
                    print(self.data)
        except ValueError as e:
            self.__sock.close()
            self.path = self.default_path
            self.name = self.default_name
            self.address = self.default_address
            self.connected = False
            print("Server stop responding disconnected from server")

    def send_data(self, data: str) -> bool:

        try:
            length = len(data)
            self.__sock.send(str(length).encode())
            assert (int(self.__sock.recv(1024).decode("utf-8")) == length), "error with sending length"
            self.__sock.send(data.encode())
            assert (self.__sock.recv(1024).decode("utf-8") == "True"), "Problem with answer from server"
            t = self.__sock.recv(1024).decode("utf-8")
            print("Data transfer complete in {}".format(t))
            return True
        except AssertionError as e:
            print(e)
            return False

    def receive_data(self):
        length = int(self.__sock.recv(1024).decode("utf-8"))
        t = clock()
        self.__sock.send(str(length).encode())
        self.data = self.__sock.recv(2048).decode("utf-8")
        if len(self.data) == length:
            answer = True
        else:
            answer = False

        self.__sock.send(str(answer).encode())
        self.__sock.send(str(clock() - t).encode())


client = Client(manual)
client.run()
