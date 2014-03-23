import argparse
import subprocess 

def run_pesq(args):
	pesq_command = "./pesq +16000 " + args.original_file + " " + args.recorded_file + " | grep \'P.862 Prediction (Raw MOS, MOS-LQO):\'"
	print "pesq_command: ", pesq_command
	subprocess.call([pesq_command], shell=True)
	return

def execute_pesq(original_file, recorded_file):
	pesq_command = "./pesq_tools/pesq +16000 " + original_file + " " + recorded_file + " | grep \'P.862 Prediction (Raw MOS, MOS-LQO):\'"
	#print "pesq_command: ", pesq_command
	subprocess.call([pesq_command], shell=True)
	return

def make_args_parser():
	parser = argparse.ArgumentParser(version='%prog 0.1',
					 description='''run_pesq: PESQ runner
USAGE:
<original_file> <degraded_file>
									''')

	parser.add_argument("original_file", help="original file path")
	parser.add_argument("recorded_file", help="recorded file path")

	return parser

if __name__ == '__main__':
	args = make_args_parser().parse_args()
	run_pesq(args)