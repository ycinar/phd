import os
from os import listdir
from os.path import isfile, join

time_diff_file_path = './time_diff'
app_data = "/home/ycinar/webrtc/"
measured_time_diff_path = app_data + "time_diff"

def prep():
	try:
		os.remove(time_diff_file_path)
	except OSError:
		pass

def get_time_diff(exec_no, min_delay, max_delay):
	time_diff_list = calculate_time_diff()
	if len(time_diff_list) > 0:
		with open("%s_%s_%s_%s" % (measured_time_diff_path, str(min_delay), str(max_delay), str(exec_no)), 'a+') as time_diff_file:
			for td in time_diff_list:
				time_diff_file.write(str(td) + "\n")
			time_diff_file.close()

def calculate_time_diff():

	# prepare environment first
	prep()
	###########################

	rtp_folder = "./rtp/"
	rtp_files = listdir(rtp_folder)

	time_stamps = list()
	time_diff = list()

	print "rtp_folder" + rtp_folder
	print rtp_files[:2]

	if len(rtp_files) > 0:
		with open(rtp_folder + max(rtp_files, key=len), "r") as results_file:
			for line in results_file:
				time_stamps.append(float(line.split()[0]))
		results_file.close()
	else:
		print "error: no rtp log file was created"
		return time_diff

	#print time_stamps[:15]

	for t in time_stamps:
		idx = time_stamps.index(t)
		if idx+1 != len(time_stamps):
			time_diff.append( int((time_stamps[idx+1] - t) * 1000) )

	with open(time_diff_file_path, 'a+') as time_diff_file:
		for td in time_diff:
			time_diff_file.write(str(td) + "\n")
		time_diff_file.close()

	#print time_diff[0:50]
	return time_diff

def add_to_file(path, flag, text):
	current_file = open(path, flag)
	current_file.write(text)
	current_file.close()

def calculate_tranmission_delay():

	caller_folder = app_data + "caller/"
	callee_folder = app_data + "callee/"

	caller_files = listdir(caller_folder)
	callee_files = listdir(callee_folder)

	if len(caller_files) > 0 and len(callee_files) > 0:
		for caller_file in caller_files:
			print "processing ", caller_file
			time_stamps_caller = list()
			time_stamps_callee = list()			
			with open (caller_folder + caller_file) as rtp_file:
				for line in rtp_file:
					time_stamps_caller.append(float(line.split()[0]))
			with open (callee_folder + caller_file) as rtp_file:
				for line in rtp_file:
					time_stamps_callee.append(float(line.split()[0]))
			for time_stamp_caller, time_stamp_callee in zip(time_stamps_caller, time_stamps_callee):
				tranmission_delay = str(int((time_stamp_callee - time_stamp_caller - 34.9) * 1000))
				record = "%s 	%s 	%s\n" % (time_stamp_callee, time_stamp_caller, tranmission_delay)
				file_name = app_data + "tranmission_delay_" + caller_file
				add_to_file(file_name, "a+", record)
				
	else:
		print "len(callee_files): ", len(callee_files)
		print "len(caller_files): ", len(caller_files)
		print "exit"

if __name__ == '__main__':
	calculate_time_diff()
