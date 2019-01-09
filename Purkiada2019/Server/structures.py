# -*- encoding: utf-8 -*-

############################################

# Creating structures

############################################


class Directory:

    def __init__(self, name: str, permissions: list,
                 upper_directory, owner, group):
        self.name = name
        self.owner = owner
        self. group = group
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
        elif user.group.name == self.group:
            return self.check_permission(permission, 1)
        else:
            return self.check_permission(permission, 2)

    def ls(self, user) -> list:
        if self.validate(user, "r"):
            return self.__content
        else:
            return []


class File:

    def __init__(self, name: str, content: str,
                 permissions: str, owner, group):
        self.type = "file"
        self.name = name
        self.owner = owner
        self.group = group
        self.__content = content
        self.permissions = permissions

    def read(self) -> str:
        return self.__content

    def __str__(self) -> str:
        return self.name
