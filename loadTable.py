import xlrd

fileLocation = "c:\\temp\\table.xlsx"
workbook = xlrd.open_workbook(fileLocation)
sheet = workbook.sheet_by_index(0)
#sheet.cell_value(0,0)
#print(sheet.nrows)
#print(sheet.ncols)
data = [[sheet.cell_value(r,c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]

users = []
for i in range(1, len(data)):
    users.append(data[i][4])#1
#print("Users: {}\n".format(users))

pswds = []
for i in range(1, len(data)):
    pswds.append(data[i][3])#2
#print("Pswds: {}".format(pswds))import xlrd

file = open("usersFromTable.txt", "w")
for user in users:
    if user != "":
        try:
            file.write("{}-{}\n".format(user, pswds[users.index(user)]))
        except:
            print("Error with saving user \"{}\"".format(user))
file.close()
