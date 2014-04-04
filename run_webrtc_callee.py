import run_webrtc_executable
import socket
import threading
import json
import packet_monitor
import report

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
	handle_test_instruction()

if __name__ == '__main__':
	main()