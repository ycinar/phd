results_file_path = "./receivedmsgs"

time_stamps = list()

with open(results_file_path, "r") as results_file:
	for line in results_file:
		if (line[-1:]=='\n'): 
			time_stamps.append(line[:-1])
		else:
			time_stamps.append(line)

print time_stamps

if time_stamps == sorted(time_stamps):
	print 'original list is sorted'
else:
	print 'original list is not sorted'
	for x, y in zip (time_stamps, sorted(time_stamps)):
		if (x!=y):
			print 'Difference... x:%s y:%s' % (x,y)
			break

if sorted(time_stamps) == sorted(time_stamps,reverse=True):
	print 'something is wrong'
