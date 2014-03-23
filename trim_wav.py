import subprocess
import glob
import os
import shutil

def extract_last_five(path):
	wav_files = glob.glob(path)

	#print wav_files
	command1 = "sox %s %s reverse trim 0 6"
	command2 = "sox %s %s reverse trim 0 6"
	
	for wav_file in wav_files:
		command =  command1 % (wav_file, wav_file + "_reverse_extracted.wav")
		#print command
		subprocess.call(command, shell=True)
		command =  command1 % (wav_file + "_reverse_extracted.wav", wav_file + "_extracted.wav")
		#print command
		subprocess.call(command, shell=True)

		if not os.path.exists(path[:-5] + "extracted/"):
		    os.makedirs(path[:-5] + "extracted/")

		shutil.copy(wav_file + "_extracted.wav", path[:-5] + "extracted/")

		os.remove(wav_file + "_reverse_extracted.wav")
		os.remove(wav_file + "_extracted.wav")

if __name__ == '__main__':
	extract_last_five('/home/ycinar/dev/phd/temp/*.wav')