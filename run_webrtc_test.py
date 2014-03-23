import os
import subprocess 
from random import randint
import threading
import shutil
import json
import datetime

# local libraries
import time_diff

workspace = ""
app_data = "/home/ycinar/webrtc/"
results_file_path = app_data + "pesq_results" # need to hard code as it is in hardcoded in the C++ application
current_test_config = app_data + "current_test_config"
jitter_output_file = app_data + "desired_jitter_output"
measured_time_diff_path = app_data + "time_diff"
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


	dummynet_command = "sudo ipfw add 100 pipe 1 ip from 127.0.0.1 to 127.0.0.1 in"
	subprocess.call([dummynet_command], shell=True)
	dummynet_command = "sudo ipfw add 100 allow ip from 127.0.0.1 to 127.0.0.1 out"
	subprocess.call([dummynet_command], shell=True)
	dummynet_command = "sudo ipfw pipe 1 config delay 1ms" # doesnt work without this
	subprocess.call([dummynet_command], shell=True)	

	subprocess.call(["sudo tc qdisc add dev lo root handle 1: netem delay 1ms"], shell=True)

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
		packet_mon_thread = PacketMonitor('packet_mon')
		packet_mon_thread.start()
		add_to_file(current_test_config, "w", "%d_%d_%d" % (min_delay, max_delay, x))
		subprocess.call([test_command], shell=True)
		print "Completed the execution..."
		calculate_time_diff(x)
		clearPacketMonitor(x)

def add_to_file(path, flag, text):
	current_file = open(path, flag)
	current_file.write(text)
	current_file.close()

class PacketMonitor(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		#self.threadID = threadID
		self.name = name
		self.shutdown = False
	def run(self):		
		print "Starting " + self.name
		conmon_string = "sudo conmon lo udp --rtp"
		os.system(conmon_string)
		print "Exiting " + self.name

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

def calculate_time_diff(exec_no):
	time_diff_list = time_diff.calculate_time_diff()
	if len(time_diff_list) > 0:
		with open("%s_%s_%s_%s" % (measured_time_diff_path, str(min_delay), str(max_delay), str(exec_no)), 'a+') as time_diff_file:
			for td in time_diff_list:
				time_diff_file.write(str(td) + "\n")
			time_diff_file.close()

def clearPacketMonitor(exec_no):
	os.system("sudo kill -9 $(pidof conmon)")

	rtp_files = os.listdir(rtp_folder)

	if len(rtp_files) > 0:
		print "clearPacketMonitor: There are rtp files, number of files: ", len(rtp_files)
		shutil.copy(rtp_folder + max(rtp_files, key=len), app_data + 'rtp_' + "%s_%s_%s" % (str(min_delay), str(max_delay), str(exec_no)) )
		for rtp_file in rtp_files:
			os.remove(rtp_folder + rtp_file)		
	else:
		print "clearPacketMonitor: There is no rtp file."

def run_scenarios():
	# add header
	add_to_file(results_file_path, "a", "Date-time: " + datetime.datetime.now().time() .isoformat() + "\n")

	global min_delay
	global max_delay

	try:
		for delay in delay_list:
			min_delay = int(delay[0])
			max_delay = min_delay + int(delay[1])
			print "Starting the tests for (%d,%d)" % (min_delay, max_delay)
			add_to_file(results_file_path, "a", "Results with network config min_delay: %d  max_delay: %d\n" % (min_delay, max_delay))
			jitter_thread = JitterThread('jitter_thread')
			jitter_thread.shutdown = False
			jitter_thread.start()
			execute_test()
			jitter_thread.shutdown = True
			jitter_thread.join()			
	except(KeyboardInterrupt, SystemExit):
	        os.sys.exit("Interrupted by ctrl+c\n")
	'''	
	# change the network config
	subprocess.call(["sudo tc qdisc add dev lo root netem delay 100ms 50ms"], shell=True)
	add_header_for_test_case("Results with 100ms 50ms\n")
	execute_test()
	'''

def report_results():
	#report the pesq file
	with open(results_file_path, "r") as results_file:
		for line in results_file:
			print line
	results_file.close()

	merge_time_diff_files()

	sort_max_delay_values()

	analyze_extracted_wav_files()

def analyze_extracted_wav_files():
	import trim_wav
	#app_data = "/home/ycinar/webrtc/"
	reference_file = "./human-voice-linux-extracted.wav"
	trim_wav.extract_last_five(app_data + "*.wav")

	import glob
	extracted_files = glob.glob(app_data + "extracted/*.wav")
	print extracted_files

	pesq_results = dict()
	for extracted_file in extracted_files:
		print extracted_file
		if "human-voice-linux" in extracted_file: 
			continue
		min_delay, max_delay, execution = extracted_file[len(app_data + "extracted/"):].split("_")[:3]
		print min_delay, max_delay, execution[:-4]
		#print min_delay + "_" + max_delay

		import sys
		sys.path.append("./pesq_tools/")
		import run_pesq
		run_pesq.execute_pesq(reference_file, extracted_file)

		result = 1
		pesq_results[min_delay + "_" + max_delay] = [execution[:-4], result]

	print pesq_results


def sort_max_delay_values():
	#time_diff_max_values_path = '/home/ycinar/webrtc/time_diff_max_values'
	#time_diff_max_sorted_path = '/home/ycinar/webrtc/time_diff_max_sorted'
	# max values are already written to time_diff_max_values for each execution
	# this function sorts these values and writes to time_diff_max_sorted
	json_data = open(time_diff_max_values_path, "r+")
	json_data_string = json_data.read()
	json_data.seek(0)
	json_data.write(json_data_string.replace('\'', '\"'))
	json_data.seek(0)	
	json_data = open(time_diff_max_values_path)
	data = json.load(json_data)
	#print "data", data
	import operator
	sorted_data = sorted(data.iteritems(), key=operator.itemgetter(1), reverse=True)
	#for key, value in sorted_data:
	#	print key, value
	json_data.close()
	add_to_file(time_diff_max_sorted_path, 'a', str(sorted_data))


def merge_time_diff_files():
	import glob

	time_diff_dict = dict()
	time_diff_list = list()
	max_no_in_list = 0
	time_diff_files = glob.glob(app_data + "time_diff_*")

	diff_max_dict = dict()

	for time_diff_file in time_diff_files:
		with open(time_diff_file) as tdf:
			for line in tdf:
				time_diff_list.append(int(line))
			time_diff_dict[time_diff_file[len(app_data + 'time_diff_'):]] = time_diff_list
			diff_max_dict['max_' + time_diff_file[len(app_data + 'time_diff_'):]] = max(time_diff_list)
			if len(time_diff_list) > max_no_in_list:
				max_no_in_list = len(time_diff_list)
			time_diff_list = []

	print diff_max_dict
	add_to_file(time_diff_max_values_path, 'a', str(diff_max_dict))

	value_to_print = ''
	for key in time_diff_dict.keys():
		value_to_print += "%-12s" % key
	add_to_file(time_diff_merged_path, 'a', value_to_print + '\n')

	for x in range(0, max_no_in_list):
		current_row = []
		for key in time_diff_dict.keys():
			if x >= len(time_diff_dict[key]):
				current_row.append(-1)
			else:
				current_row.append(time_diff_dict[key][x])
		value_to_print = ''
		for value in current_row:
			value_to_print += "%-12d" % value
		#print value_to_print
		add_to_file(time_diff_merged_path, 'a', value_to_print + '\n')


if __name__ == '__main__':
	prep_env()
	read_jitter_config()
	run_scenarios()
	report_results()
	subprocess.call(["sudo tc qdisc del dev lo root"], shell=True)
	subprocess.call(["sudo ipfw pipe 1 delete"], shell=True)
	subprocess.call(["sudo ipfw -q flush"], shell=True)
	os.sys.exit