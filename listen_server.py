import socket
import threading
soc = socket.socket()
soc.bind(("0.0.0.0",9601))
soc.listen(1)
def handler(c, a):
	c.send(" This is password for admin(in binary): 01101110 01100101 01101111 01110000 01101001 01110011 01110101 01101010 01110101 00110010 00110000 00110001 00111000".encode())
	c.close()
while True:
	c, a = soc.accept()
	cThread = threading.Thread(target = handler, args = (c, a))
	cThread.daemon = True
	cThread.start()