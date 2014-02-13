import os
import subprocess 
from random import randint

results_file_path = "/home/ycinar/okul/src/out/Debug/pesq_results"
test_command = "/home/ycinar/okul/src/out/Debug/browser_tests --gtest_filter=WebrtcAudioQualityBrowserTest.MANUAL_TestAudioQuality --single_process"
def execute_test():
	# execute the tests
	for x in range(0,5):
		print "Start the test no:%d" % (x)
		subprocess.call([test_command], shell=True)
		print "Completed the test..."

def add_header_for_test_case(header):
	results_file = open(results_file_path, "a")
	results_file.write(header)
	results_file.close()

def netem_jitter():	
	delay = randint(50,500)
	print "delay: ", delay
	netem_command = "sudo tc qdisc change dev lo root handle 1: netem delay %dms" % delay
	subprocess.call([netem_command], shell=True)

def run_scenarios():
	# remove the results file
	try:
		os.remove(results_file_path)
	except OSError:
		pass

	# add header
	add_header_for_test_case("Results with no network config\n")

	# execute the tests
	execute_test()

	'''
	# change the network config
	subprocess.call(["sudo tc qdisc add dev lo root netem delay 100ms 50ms"], shell=True)
	add_header_for_test_case("Results with 100ms 50ms\n")
	execute_test()
	
	subprocess.call(["sudo tc qdisc add dev lo root netem delay 100ms 100ms"], shell=True)
	add_header_for_test_case("Results with 100ms 100ms\n")
	execute_test()

	subprocess.call(["sudo tc qdisc add dev lo root netem delay 100ms 150ms"], shell=True)
	add_header_for_test_case("Results with 100ms 150ms\n")
	execute_test()
	'''

def report_results():
	#open the file
	with open(results_file_path, "r") as results_file:
		for line in results_file:
			print line

	results_file.close()

if __name__ == '__main__':
	run_scenarios()
	report_results()
	subprocess.call(["sudo tc qdisc del dev lo root"], shell=True)
