import os
import subprocess 
from random import randint
import threading
import shutil
import json
import datetime
import time
import socket
import packet_monitor
import report

# local libraries
import time_diff

workspace = ""
app_data = "/home/ycinar/webrtc/"
results_file_path = app_data + "pesq_results" # need to hard code as it is in hardcoded in the C++ application
current_test_config = app_data + "current_test_config"
jitter_output_file = app_data + "desired_jitter_output"
time_diff_merged_path = app_data + 'time_merged_diff'
time_diff_max_values_path = app_data + 'time_diff_max_values'
time_diff_max_sorted_path = app_data + 'time_diff_max_sorted'
rtp_folder = "./rtp/"
packet_logs_folder = "./logs/"
test_command = ""
min_delay = 1
max_delay = 1
current_execution_no = 0
number_of_execution_for_each_scenario = 1
delay_list = list()
delay_array = [30, 100, 40, 60, 44, 99, 125, 180, 20, 80, 14, 54, 140, 190, 100, 23, 54, 180, 160, 100, 10, 140, 40, 21, 140, 10, 130, 10, 60, 160, 144, 19, 25, 180, 120, 18, 114, 24, 140, 140, 100, 123, 154, 180, 16, 10, 104, 141, 40, 121, 14, 100, 190]
delay_profile = list()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
jitter_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
BUFFER_SIZE = 1024

def prep_env():
	global workspace
	global test_command

	if os.path.isdir("/home/ycinar/dev/src/out/Debug/"):
		workspace = "/home/ycinar/dev/src/out/Debug/"
	elif os.path.isdir("/home/ycinar/okul/src/out/Debug/"):
		workspace = "/home/ycinar/okul/src/out/Debug/"
	else:
		print "workspace is not found - script will fail"
	print "workspace: ", workspace	
	test_command = workspace + "browser_tests --gtest_filter=WebrtcAudioQualityBrowserTest.MANUAL_TestAudioQuality --single_process"

	if os.path.exists(app_data):
		shutil.rmtree(app_data)
	
	os.makedirs(app_data)

	open(results_file_path, 'a').close()
	open(current_test_config, 'a').close()
	
	if not os.path.exists(rtp_folder):
	    os.makedirs(rtp_folder)

	if not os.path.exists(packet_logs_folder):
	    os.makedirs(packet_logs_folder)

	if os.path.exists("./pesq_results.txt"):
		os.remove("./pesq_results.txt")

	dummynet_command = "sudo ipfw add 100 pipe 1 ip from any to any in"
	subprocess.call([dummynet_command], shell=True)
	dummynet_command = "sudo ipfw add 100 allow ip from any to any out"
	subprocess.call([dummynet_command], shell=True)
	dummynet_command = "sudo ipfw pipe 1 config delay 1ms" # doesnt work without this
	subprocess.call([dummynet_command], shell=True)	

	#subprocess.call(["sudo tc qdisc add dev lo root handle 1: netem delay 1ms"], shell=True)

def read_jitter_config():
	global delay_list
	global number_of_execution_for_each_scenario

	json_data = open('jitter_config')
	data = json.load(json_data)

	number_of_execution_for_each_scenario = data['number_of_execution_for_each_scenario']
	
	for delay in data['delay']:
		delay_list.append(delay)

	json_data.close()

def execute_test():
	# execute the tests
	print test_command
	for x in range(0,number_of_execution_for_each_scenario):
		global current_execution_no
		current_execution_no = x
		print "Start the execution no:%d" % (x)
		packet_mon_thread = packet_monitor.PacketMonitor('packet_mon')
		packet_mon_thread.start()
		add_to_file(current_test_config, "w", "%d_%d_%d" % (min_delay, max_delay, x))
		request_callee_start(min_delay, max_delay, x)
		import run_webrtc_executable
		run_webrtc_executable.start_caller_process()
		print "Completed the execution..."
		packet_monitor.stop_packet_monitor_and_get_time_diff(x, min_delay, max_delay)
		is_callee_finished()

def add_to_file(path, flag, text):
	current_file = open(path, flag)
	current_file.write(text)
	current_file.close()

class JitterThread(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		#self.threadID = threadID
		self.name = name
		self.shutdown = False
	def run(self):		
		print "Starting " + self.name
		import itertools
		while not self.shutdown:
		#for delay_val in itertools.cycle(delay_array):
			execute_dummynet()
			#execute_netem()
		#	if self.shutdown:
		#		break
		print "Exiting " + self.name
		for time_delay in delay_profile:
			add_to_file ("%s_%s_%s" % (jitter_output_file, str(min_delay), str(max_delay)), "a", str(time_delay) + "\n")
		global delay_profile
		delay_profile = []

def execute_netem():
	delay = randint(min_delay, max_delay)
	netem_command = "sudo tc qdisc change dev lo root handle 1: netem delay %dms" % delay
	subprocess.call([netem_command], shell=True)

def execute_dummynet():
	delay = randint(min_delay, max_delay)
	#add_to_file(jitter_output_file, "a", datetime.datetime.now().time().isoformat() + " " + str(delay) + "\n")
	global delay_profile
	delay_profile.append((datetime.datetime.now().time().isoformat(), delay))	
	dummynet_command = "sudo ipfw pipe 1 config delay %dms" % delay
	#subprocess.call([dummynet_command], shell=True)
	os.system(dummynet_command)

def setup_connections():
	TCP_IP = '10.53.59.66' # caller ip address
	TCP_PORT = 5007
	s.connect((TCP_IP, TCP_PORT))

	TCP_IP = '10.61.212.125' # jitter handler ip adress
	TCP_PORT = 5008
	jitter_connection.connect((TCP_IP, TCP_PORT))

def send_message(connection, data):
	print "sending: ", data
	connection.send(data)
	data = connection.recv(BUFFER_SIZE)
	print "received data:", data	
	return data

def recv_message_from_callee(connection):
	data = connection.recv(BUFFER_SIZE)
	print "received data:", data
	return data

def request_callee_start(current_min_delay, current_max_delay, current_execution_no):
	execution_config = {'command': 'START_CALLEE', 
						'min_delay': current_min_delay, 
						'max_delay': current_max_delay, 
						'execution_no': current_execution_no
						}
	send_message(s, json.dumps(execution_config))
	time.sleep(2)

def is_callee_finished():
	print "Waiting for callee to finish"
	data = recv_message_from_callee(s)
	print "callee returned"
	if data == "FINISHED_CALLEE":
		return True
	return False

def start_jitter():
	jitter_config = {'command': 'START_JITTER',
					 'min_delay': min_delay,
					 'max_delay': max_delay
					}
	send_message(jitter_connection, json.dumps(jitter_config))

def stop_jitter():
	jitter_config = {'command': 'STOP_JITTER'}
	send_message(jitter_connection, json.dumps(jitter_config))

def run_scenarios():
	# add header
	add_to_file(results_file_path, "a", "Date-time: " + datetime.datetime.now().time() .isoformat() + "\n")

	global min_delay
	global max_delay

	setup_connections()

	try:
		for delay in delay_list:
			min_delay = int(delay[0])
			max_delay = min_delay + int(delay[1])
			print "Starting the tests for (%d,%d)" % (min_delay, max_delay)
			add_to_file(results_file_path, "a", "Results with network config min_delay: %d  max_delay: %d\n" % (min_delay, max_delay))
			if min_delay != 0:
				start_jitter()
			execute_test()
			if min_delay != 0:			
				stop_jitter()
	except(KeyboardInterrupt, SystemExit):
	        os.sys.exit("Interrupted by ctrl+c\n")


if __name__ == '__main__':
	prep_env()
	read_jitter_config()
	run_scenarios()
	report.report_results()
	subprocess.call(["sudo tc qdisc del dev lo root"], shell=True)
	subprocess.call(["sudo ipfw pipe 1 delete"], shell=True)
	subprocess.call(["sudo ipfw -q flush"], shell=True)
	os.sys.exit