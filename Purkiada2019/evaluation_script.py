# -*- coding: utf-8 -*-
from os import listdir
import xlrd


class User:

    def __init__(self, id, name, last_name, login, path):
        self.id = id
        self.name = name
        self.last_name = last_name
        self.login = str(int(login))
        self.history = None
        self.path = path
        self.history_path = None
        self.work_over_time = False
        self.work_from_home = False
        self.was_connected = False
        self.points = 0
        self.finished_quests = 0
        self.finished_quests_list = []

        self.set_history_path()

    def set_history_path(self):
        self.history_path = self.path + self.login + "_log.Log"

    def open_history(self):
        with open(self.history_path, "r") as file:
            f = file.readlines()
            self.history = f

    def get_result(self, final_date, school_address):
        for line in self.history:
            address, daytime, month, day, time, year, command, *argument = line.split(" ")
            date = "{} {} {} {} {}".format(daytime, month, day, time, year)

            if type(argument) == list:
                argument = argument[0]
            argument = argument.lower()
            argument = argument.replace("\n", "")
            argument = argument.replace("[\'", "")
            argument = argument.replace("\']", "")
            argument = argument.replace(" ", "")
            command = command.split(":")[1]

            if address.split(":")[0] == school_address:
                if date < final_date:
                    if command == "submit":
                        if argument == "undf":

                            self.points += 3
                            self.finished_quests += 1
                            self.finished_quests_list += "1"

                        if argument == "purkiada":
                            self.points += 3
                            self.finished_quests += 1
                            self.finished_quests_list += "2"

                        if argument == "...-\',":
                            self.points += 1.5
                            self.finished_quests += 1
                            self.finished_quests_list += "2"

                        if argument == "vsechno":
                            self.points += 2
                            self.finished_quests += 1
                            self.finished_quests_list += "3"

                        if argument == "2019":
                            self.points += 1
                            self.finished_quests += 1
                            self.finished_quests_list += "4"

                else:
                    self.history.remove(line)
                    self.work_over_time = True
            else:
                self.work_from_home = True\

        if self.work_over_time:
            print("user {} was working over time, ended at {}".format(self.name, date))
            self.points = 0
        elif self.work_from_home:
            print("user {} was working outside school from {}".format(self.name, address))
            self.points = 0
        else:
            pass
            # print("user {} {} wasn't cheating".format(self.name, self.last_name))


class Validator:

    def __init__(self, log_path, user_table, final_date, school_address):
        self.final_date = final_date
        self.school_address = school_address
        self.log_path = log_path
        self.user_table = user_table
        self.users_login = None
        self.user_table = None
        self.workbook = None
        self.sheet = None
        self.data = None
        self.users = []
        self.ids = []
        self.users_names = []
        self.users_last_names = []
        self.users_logins = []
        self.set_users_login()
        self.set_user_table(user_table)
        self.validate()

    def set_users_login(self):
        temp = listdir(self.log_path)
        for i in range(len(temp)):
            temp[i] = temp[i][:4]

        self.users_login = temp

    def set_user_table(self, table_path):
        try:
            self.workbook = xlrd.open_workbook(table_path)
            self.sheet = self.workbook.sheet_by_index(0)
            self.data = [[self.sheet.cell_value(r, c)
                         for c in range(self.sheet.ncols)]
                         for r in range(self.sheet.nrows)]
        except FileNotFoundError as e:
            print(e)
            self.data = ""

        for i in range(1, len(self.data)):
            self.ids.append(str(int(self.data[i][0])))

        for i in range(1, len(self.data)):
            self.users_names.append(self.data[i][1])

        for i in range(1, len(self.data)):
            self.users_last_names.append(self.data[i][2])

        for i in range(1, len(self.data)):
            self.users_logins.append(self.data[i][9])

    def validate(self):
        for i in range(len(self.ids)):
            user = User(self.ids[i], self.users_names[i], self.users_last_names[i], self.users_logins[i], self.log_path)
            self.users.append(user)
        for user in self.users:
            if user.login in self.users_login:
                user.open_history()
                user.was_connected = True
                user.points += 1
                user.get_result(self.final_date, self.school_address)

        for passnum in range(len(self.users) - 1, 0, -1):
            for i in range(passnum):
                if self.users[i].points < self.users[i + 1].points:
                    temp = self.users[i]
                    self.users[i] = self.users[i + 1]
                    self.users[i + 1] = temp

        for user in self.users:
            if user.points > 0:
                print("""user:{!s} {!s} get {}  points  with login: {} and complete {} objectives""".format(user.name, user.last_name,
                                                               user.points, user.login,
                                                               user.finished_quests))


validator = Validator("Server/users/history/",
                      "Server/users/table_final.xlsx",
                      "Wed Jan 30 12:10:00 2019", "147.229.242.34")
