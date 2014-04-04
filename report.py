import json

app_data = "/home/ycinar/webrtc/"
results_file_path = app_data + "pesq_results"
time_diff_merged_path = app_data + 'time_merged_diff'
time_diff_max_values_path = app_data + 'time_diff_max_values'
time_diff_max_sorted_path = app_data + 'time_diff_max_sorted'

def add_to_file(path, flag, text):
	current_file = open(path, flag)
	current_file.write(text)
	current_file.close()

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
		#print extracted_file
		if "human-voice-linux" in extracted_file: 
			continue
		min_delay, max_delay, execution = extracted_file[len(app_data + "extracted/"):].split("_")[:3]
		#print min_delay, max_delay, execution[:-4]

		import sys
		sys.path.append("./pesq_tools/")
		import run_pesq
		run_pesq.execute_pesq(reference_file, extracted_file)

		#result = 1 # get the result from run_pesq.execute_pesq 
		#pesq_results[min_delay + "_" + max_delay] = [execution[:-4], result]

	#print pesq_results

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
