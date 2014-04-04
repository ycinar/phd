import os
import subprocess 

workspace = ""
app_data = "/home/ycinar/webrtc/"
callee_command = ""
caller_command = ""

def prep_env():
	global workspace
	global test_command
	global caller_command
	global callee_command

	if os.path.isdir("/home/ycinar/dev/src/out/Debug/"):
		workspace = "/home/ycinar/dev/src/out/Debug/"
	elif os.path.isdir("/home/ycinar/okul/src/out/Debug/"):
		workspace = "/home/ycinar/okul/src/out/Debug/"
	else:
		print "workspace is not found - script will fail"
	print "workspace: ", workspace	
	callee_command = workspace + "browser_tests_callee --gtest_filter=WebrtcAudioQualityBrowserTest.MANUAL_TestAudioQuality --single_process"
	caller_command = workspace + "browser_tests_caller --gtest_filter=WebrtcAudioQualityBrowserTest.MANUAL_TestAudioQuality --single_process"

def start_callee_process():
	prep_env()
	subprocess.call([callee_command], shell=True)
	print "execution completed"
	return

def start_caller_process():
	prep_env()
	subprocess.call([caller_command], shell=True)
	print "execution completed"
	return

if __name__ == '__main__':
	start_callee_process()