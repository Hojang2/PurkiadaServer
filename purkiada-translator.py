print("For exit type \"exit\"")
while True:
    data = input("write binary text: ")
    if data == "exit":
        break
    data = data.split(" ")
    for i in data:
        print(chr(int(i, 2)),end="")
    print()
