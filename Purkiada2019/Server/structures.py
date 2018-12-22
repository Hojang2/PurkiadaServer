# -*- encoding: utf-8 -*-

############################################

# Creating structures

############################################


class Directory:

    def __init__(self, name: str, permissions: str, upper_directory):
        self.name = name
        self.path = self.name + "/"
        self.type = "directory"
        self.__content = []
        self.permissions = permissions
        self.upper_directory = upper_directory

    def __str__(self) -> str:
        return self.name

    def add(self, new_content) -> None:
        new_content.path = self.path + new_content.path
        self.__content.append(new_content)

    def validate(self, permission: str) -> bool:
        if permission[2] == self.permissions[2]:
            return True
        else:
            return False

    def ls(self, permission: str) -> list:
        if self.validate(permission):
            return self.__content
        else:
            return []


class File:

    def __init__(self, name: str, content: str, permissions: str):
        self.type = "file"
        self.name = name
        self.__content = content
        self.permissions = permissions

    def read(self) -> str:
        return self.__content

    def __str__(self) -> str:
        return self.name
