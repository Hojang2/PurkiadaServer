import socket
import time
#-*- encoding: utf-8 -*-
actions = ["ls","ssh","help","listen","exit","cd","disconnect", "read","bcad"]

def showHelp():
    print("------------------------------------------------")
    print("for help write \"help\"")
    print(" ssh [ip]:[port]\" - connect to server")
    print(" listen [ip]:[port]\" - listen to server")
    print(" dir - show you content of folder")
    print(" cd [directory name] - change working directory")
    print(" cd ..  - go to the upper folder")
    print(" cd /  - go to the start")
    #print(" rm - rename something")
    print(" bcad [password]  - will make you admin")
    print(" disconnect - say \"bye!\" to server")
    print(" exit - close this application")
    print("------------------------------------------------")

showHelp()
connect = False
print("now let's start write action")
conected=False
path = ""
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    action = input(path+"~$ ")
    action = action.split(" ")
    if len(action) < 2 and (action[0] == "cd" or action[0] == "read" or action[0] == "bcad"):
        print("mising argument")
        action=["None","None"]
    if connect == True and (action[0] == "ssh" or action[0] == "listen"):
        print("You can't connect when you are connected to server")
    if  connect != True:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if action[0] == "ssh":
            if action[1] != "193.165.214.38:9601":
                try:
                    adr, port = action[1].split(":")
                    soc.connect((adr,int(port)))
                    connect = True
                    print("new connection with "+adr+" on port: "+str(port))
                    print(soc.recv(4024).decode("utf8"))
                    pom = soc.recv(1024).decode("utf8")
                    for i in range(1):
                        user_name = input("username: ")
                        password = input("password: ")
                        soc.send("{0}-{1}".format(user_name,password).encode())
                        answ = soc.recv(1024).decode("utf8")
                        if answ == "True":
                            print("Welcome user " + user_name)
                            conected = True
                            path = pom
                        else:
                            connect = False
                            print("Invalid username or password")
                except:
                    print("wrong adress or port")


        if action[0] == "listen":
            if action[1] != "193.165.214.38:9600":
                try:
                    adr, port = action[1].split(":")
                    soc.connect((adr,int(port)))
                    print("server found, listening on port:"+str(port)+"\n")
                    b_data=soc.recv(2048).decode("utf8")
                    print(b_data)
                except:
                    print("host not found")
    if action[0] == "help":
        showHelp()
    if action[0] == "exit" and connect == True:
        path = ""
        connect = False
        conected = False
        soc.send("disconnect".encode())
        soc.close()
        exit()

    if action[0] == "exit" and connect == False:
        exit()

    if action[0] == "disconnect" and connect == True:
        path = ""
        connect=False
        conected = False
        soc.send(action[0].encode())
        soc.close()
    if action[0] not in actions:
        print("unknown command")

    if connect and conected:
        if action[0] == "ls":
            soc.send("ls".encode())

            permission = soc.recv(1024).decode("utf8")
            if permission == "True":
                data=soc.recv(1024).decode("utf8")
                data = data.split(" ")
                for i in data:
                    if i != " ":
                        print(i)
            elif permission == "False":
                print("Permission denied")
        if action[0] == "cd":
            if len(action[1]) < 500:
                soc.send((action[0]+" "+action[1]).encode())

                permission = soc.recv(1024).decode("utf8")
                if permission == "True":
                    data = soc.recv(1024).decode("utf8")
                    if data != "None":
                        path=data
                    else:
                        print(data)
                elif permission == "False":
                    print("Permission denied")
                    data = soc.recv(1024).decode("utf8")
            else:
                print("directory name is too long")
        if action[0] == "read":
            if len(action[1]) < 500:
                soc.send((action[0]+" "+action[1]).encode())

                permission = soc.recv(1024).decode("utf8")
                data = soc.recv(1024).decode("utf8")
                if permission == "True":
                    print(data)
                else:
                    print("Permission denied")
            else:
                print("file name is too long")
        """
        if action[0] == "rm":
            soc.send("rm".encode())

            permission = soc.recv(1024).decode("utf8")
            if permission == "True":
                print(soc.recv(1024).decode("utf8"))
            else:
                data = soc.recv(1024).decode("utf8")
                print("Permission denied")
        """
        if action[0] == "bcad":
            soc.send((action[0] + " " + action[1]).encode())
            permission = soc.recv(1024).decode("utf8")
            data = soc.recv(1024).decode("utf8")
            if permission == "True":
                if data == "True":
                    print("Now you are admin")
                else:
                    print("Wrong password")
            else:

                print("Permission denied")