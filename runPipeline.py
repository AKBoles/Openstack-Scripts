# this script retrieves files from Swift, renames file and then runs the pipeline from json script
# Author: Andrew Boles
import os, sys, re, json, time
import collections

def retrieveFile():
	# first need to grab file names from text file
	filenames = []
	with open('filename.txt', 'r') as f:
		for line in f:
			filenames.append(line.rstrip())
	# first I need to use os.environ to set two environmental variables for the bash script to accept --> taken from name file
	os.environ["input1"] = filenames[0]
	os.environ["input2"] = filenames[1]
	os.system('./download.sh') #need to make sure that it is executable!!!
	os.system('cp ' + filenames[0] + ' input_R1.fastq')
	os.system('cp ' + filenames[1] + ' input_R2.fastq')
	return

def renameFileName():
	with open('filename.txt') as f:
		name = f.readline().rstrip()
	name = re.sub('_.*','',name)
	os.system('mv exomecapstp8.bam ' + name+'_final.bam')
	os.environ["output1"] = name + '_final.bam'
	os.system('./upload.sh')
	return

def runPipelineCommands():
	# retrieve the text file names to be processed, change them accordingly
	retrieveFile()
	# Open the config file containing the commands, load into ordered dictionary
	command_file = open('exomecapPipeline.json')
	commands = json.load(command_file, object_pairs_hook=collections.OrderedDict)
	command_file.close()
	#Traverse through cmd config file structure
	stepNum = 1
	for step in commands:
		print('Beginning Step: %s' %stepNum)
		for cmdNum in commands[step]:
			cmd = commands[step][cmdNum] + " 2>> logfile.txt"
			os.popen(cmd)
			time.sleep(1)
			os.system('./uploadlog.sh')
			out = os.popen(cmd).read()
		stepNum = stepNum + 1
	return
logfile = open('logfile.txt', 'w')
os.system('./uploadlog.sh')
# run the function:
runPipelineCommands()
renameFileName()
print('Done processing these files. Restarting checkSwift.py')
os.system('python checkSwift.py')
