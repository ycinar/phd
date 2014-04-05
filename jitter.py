import threading
import socket
import json
import os
from random import randint

min_delay = 1
max_delay = 1

class JitterThread(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name
		self.shutdown = False
	def run(self):		
		print "Starting " + self.name
		while not self.shutdown:
			execute_dummynet()
		print "Exiting " + self.name
		#for time_delay in delay_profile:
		#	add_to_file ("%s_%s_%s" % (jitter_output_file, str(min_delay), str(max_delay)), "a", str(time_delay) + "\n")
		#global delay_profile
		#delay_profile = []

def execute_dummynet():
	delay = randint(min_delay, max_delay)
	dummynet_command = "sudo ipfw pipe 1 config delay %dms" % delay
	os.system(dummynet_command)
	#global delay_profile
	#delay_profile.append((datetime.datetime.now().time().isoformat(), delay))

def handle_jitter_instruction():
	TCP_IP = '0.0.0.0'
	TCP_PORT = 5008
	BUFFER_SIZE = 1024

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, TCP_PORT))
	s.listen(1)
	conn, addr = s.accept()
	print 'Connection address:', addr
	shutdown = False

	global min_delay
	global max_delay

	while not shutdown:
	    data = conn.recv(BUFFER_SIZE)
	    print "received data:", data
	    if not data: 
	    	print "there is no data received"
	    	break

	    data = json.loads(data)	    
	    
	    if data['command'] == 'START_JITTER':
			min_delay = data['min_delay']
			max_delay = data['max_delay']
			jitter_thread = JitterThread('jitter_thread')
			jitter_thread.shutdown = False			
			jitter_thread.start()
			conn.send('STARTED_JITTER')
			data = conn.recv(BUFFER_SIZE)
			data = json.loads(data)
			if data['command'] == 'STOP_JITTER':
				print 'stopping jitter'			
				jitter_thread.shutdown = True
				jitter_thread.join()
				conn.send("STOPED_JITTER")
			else:
				print 'UNKNOWN_INSTRUCTION'
				conn.send("UNKNOWN_INSTRUCTION")
				break			
	    else:
	    	print 'UNKNOWN_INSTRUCTION'
	    	conn.send("UNKNOWN_INSTRUCTION")
	    	break
	conn.close()

def main():
	print "starting network emulator"
	handle_jitter_instruction()

if __name__ == '__main__':
	main()