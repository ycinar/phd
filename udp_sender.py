import socket
import datetime 
import time

UDP_IP = "10.53.59.66"
UDP_PORT = 5010

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
	time.sleep(0.02)