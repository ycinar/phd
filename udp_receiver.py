import socket
import datetime
import os

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
receivedmsgs_file_path = "./receivedmsgs"

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

try:
	os.remove(receivedmsgs_file_path)
except OSError:
	pass

with open(receivedmsgs_file_path, 'a+') as msgs_file:
	while True:
	    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
	    ''' print "received message at :" + datetime.datetime.now().time().isoformat() + ": " + data '''
	    print "received message at :" + datetime.datetime.now().time().isoformat() + ": " + data
	    msgs_file.write("received message at :" + datetime.datetime.now().time().isoformat() + ": " + data + '\n')
	    sock.sendto("hello back from server!", addr)

