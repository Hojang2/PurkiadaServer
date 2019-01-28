import xlrd


class TableWorker:
    def __init__(self, table_path):
        self.table_path = table_path
        self.text_path = table_path.replace("xlsx", "txt")
        self.workbook = xlrd.open_workbook(self.table_path)
        self.sheet = self.workbook.sheet_by_index(0)
        self.users = None
        self.passwords = None
        self.data = []

    def get_table(self):
        try:
            data = [[self.sheet.cell_value(r, c)
                    for c in range(self.sheet.ncols)]
                    for r in range(self.sheet.nrows)]
        except FileNotFoundError as e:
            print(e)
            data = ""

        self.users = []
        for i in range(1, len(data)):
            self.users.append(data[i][4])

        self.passwords = []
        for i in range(1, len(data)):
            self.passwords.append(str(int(data[i][3])))

        self.data = data

    def save_text(self):
        with open(self.text_path, "w") as file:
            for user in self.users:
                if user != "":
                    file.write("{}-{}\n".format(user, self.passwords[self.users.index(user)]))

    def get_text(self):
        self.users = []
        self.passwords = []
        self.data = []
        with open(self.text_path, "r") as f:
            file = f.readlines()
            for data in file:
                data = data.replace("\n", "")
                user, password = data.split("-")
                self.users.append(user)
                self.passwords.append(password)
                self.data.append(user + " " + password)

        return self.data

    def get_data(self):
        tmp = {}

        for i in range(len(self.users)):
            tmp[str(i)] = {"name": self.users[i], "password": self.passwords[i]}

        self.data = tmp

        return self.data
