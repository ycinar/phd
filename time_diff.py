import os
from os import listdir
from os.path import isfile, join

time_diff_file_path = './time_diff'

def prep():
	try:
		os.remove(time_diff_file_path)
	except OSError:
		pass

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

if __name__ == '__main__':
	calculate_time_diff()
