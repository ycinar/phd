import os
import subprocess 
from random import randint
import threading
import shutil
import json

workspace = ""
results_file_path = "/home/ycinar/pesq_results" # need to hard code as it is in hardcoded in the C++ application
test_command = ""
min_delay = 1
max_delay = 1
number_of_execution_for_each_scenario = 1
delay_list = list()

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

	# remove the results file
	try:
		os.remove(results_file_path)
	except OSError:
		pass
		
	open(results_file_path, 'a').close()

	dummynet_command = "sudo ipfw add 100 pipe 1 ip from 127.0.0.1 to 127.0.0.1 in"
	subprocess.call([dummynet_command], shell=True)
	dummynet_command = "sudo ipfw add 100 allow ip from 127.0.0.1 to 127.0.0.1 out"
	subprocess.call([dummynet_command], shell=True)
	dummynet_command = "sudo ipfw pipe 1 config delay 1ms" # doesnt work without this
	subprocess.call([dummynet_command], shell=True)	

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
		print "Start the execution no:%d" % (x)
		subprocess.call([test_command], shell=True)
		print "Completed the execution..."

def add_header_for_test_case(header):
	results_file = open(results_file_path, "a")
	results_file.write(header)
	results_file.close()

class JitterThread(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		#self.threadID = threadID
		self.name = name
		self.shutdown = False
	def run(self):
		print "Starting " + self.name
		while not self.shutdown:
			execute_dummynet()
		print "Exiting " + self.name

def execute_netem():
	delay = randint(50,500)
	netem_command = "sudo tc qdisc change dev lo root handle 1: netem delay %dms" % delay
	subprocess.call([netem_command], shell=True)

def execute_dummynet():
	delay = randint(min_delay, max_delay)
	dummynet_command = "sudo ipfw pipe 1 config delay %dms" % delay
	subprocess.call([dummynet_command], shell=True)

def run_scenarios():
	# add header
	import datetime
	add_header_for_test_case("Date-time: " + datetime.datetime.now().time() .isoformat() + "\n")

	# 1. execute the tests no network cahnge
	add_header_for_test_case("Results with no network config\n")
	execute_test()

	global min_delay
	global max_delay

	for delay in delay_list:
		min_delay = int(delay[0])
		max_delay = min_delay + int(delay[1])
		print "Starting the tests for (%d,%d)" % (min_delay, max_delay)
		add_header_for_test_case("Results with network config min_delay: %d  max_delay: %d\n" % (min_delay, max_delay))
		jitter_thread = JitterThread('jitter_thread')
		jitter_thread.shutdown = False
		jitter_thread.start()
		execute_test()
		jitter_thread.shutdown = True
		jitter_thread.join()

	'''	
	# change the network config
	subprocess.call(["sudo tc qdisc add dev lo root netem delay 100ms 50ms"], shell=True)
	add_header_for_test_case("Results with 100ms 50ms\n")
	execute_test()
	'''

def report_results():
	#open the file
	with open(results_file_path, "r") as results_file:
		for line in results_file:
			print line

	results_file.close()
	shutil.copy(results_file_path, '.')

if __name__ == '__main__':
	prep_env()
	read_jitter_config()
	run_scenarios()
	report_results()
	subprocess.call(["sudo tc qdisc del dev lo root"], shell=True)
	subprocess.call(["sudo ipfw pipe 1 delete"], shell=True)
	subprocess.call(["sudo ipfw -q flush"], shell=True)
