import run_webrtc_executable
import socket
import threading
import json
import packet_monitor
import report
import os
import shutil

workspace = ""
app_data = "/home/ycinar/webrtc/"
results_file_path = app_data + "pesq_results" # need to hard code as it is in hardcoded in the C++ application
current_test_config = app_data + "current_test_config"
rtp_folder = "./rtp/"
packet_logs_folder = "./logs/"

def add_to_file(path, flag, text):
	current_file = open(path, flag)
	current_file.write(text)
	current_file.close()

def prep_env():
	global workspace

	if os.path.isdir("/home/ycinar/dev/src/out/Debug/"):
		workspace = "/home/ycinar/dev/src/out/Debug/"
	elif os.path.isdir("/home/ycinar/okul/src/out/Debug/"):
		workspace = "/home/ycinar/okul/src/out/Debug/"
	else:
		print "workspace is not found - script will fail"
	print "workspace: ", workspace	

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

def handle_test_instruction():
	TCP_IP = '0.0.0.0'
	TCP_PORT = 5007
	BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, TCP_PORT))
	s.listen(1)
	conn, addr = s.accept()
	print 'Connection address:', addr
	shutdown = False
	while not shutdown:
	    data = conn.recv(BUFFER_SIZE)
	    if not data: break
	    data = json.loads(data)
	    print "received data:", data
	    
	    if data['command'] == 'START_CALLEE':
			packet_mon_thread = packet_monitor.PacketMonitor('packet_mon')
			packet_mon_thread.start()
			add_to_file( current_test_config, "w", "%d_%d_%d" % ( data['execution_no'], 
																  data['min_delay'], 
																  data['max_delay'] ) )
			conn.send("STARTED_CALLEE")
			run_webrtc_executable.start_callee_process()			
			packet_monitor.stop_packet_monitor_and_get_time_diff(data['execution_no'], 
																 data['min_delay'], 
																 data['max_delay'])
			conn.send("FINISHED_CALLEE")
	    else:
	    	conn.send("UNKNOWN_INSTRUCTION")
	conn.close()
	report.report_results()

def main():
	print "Started callee"
	prep_env()
	handle_test_instruction()

if __name__ == '__main__':
	main()