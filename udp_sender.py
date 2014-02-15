import socket
import datetime 

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

current_time = datetime.datetime.now().time() 
MESSAGE = "Hello, World! Time is " + current_time.isoformat()

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE 

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

while True:
	MESSAGE = datetime.datetime.now().time() .isoformat()
	print "message:", MESSAGE 
	sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))