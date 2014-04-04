import threading
import os
import shutil
import time_diff

app_data = "/home/ycinar/webrtc/"
rtp_folder = "./rtp/"

class PacketMonitor(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		#self.threadID = threadID
		self.name = name
		self.shutdown = False
	def run(self):		
		print "Starting " + self.name
		conmon_string = "sudo conmon eth0 udp --rtp"
		os.system(conmon_string)
		print "Exiting " + self.name

def stop_packet_monitor_and_get_time_diff(exec_no, min_delay, max_delay):
	time_diff.get_time_diff(exec_no, min_delay, max_delay)

	os.system("sudo kill -9 $(pidof conmon)")

	rtp_files = os.listdir(rtp_folder)

	if len(rtp_files) > 0:
		print "clearPacketMonitor: There are rtp files, number of files: ", len(rtp_files)
		shutil.copy(rtp_folder + max(rtp_files, key=len), app_data + 'rtp_' + "%s_%s_%s" % (str(min_delay), str(max_delay), str(exec_no)) )
		for rtp_file in rtp_files:
			os.remove(rtp_folder + rtp_file)		
	else:
		print "clearPacketMonitor: There is no rtp file."