#!/usr/bin/env python
from swiftclient.multithreading import OutputManager
from swiftclient.service import SwiftError, SwiftService, SwiftUploadObject
from sys import argv

# first argument is the container to upload file to
# second argument is the number of segments to be used in
# third (and on) argument(s) is a list of the files to be uploaded
container = argv[1]
objs = []
for item in argv[3:]:
	objs.append(item)
if int(argv[2]) is 0:
	options = {}
else:
	options = {'segment_size':int(argv[2])}
with SwiftService() as swift, OutputManager() as out_manager:
    	try:
		# create the SwiftUploadObject list of objects to upload
		objs = [SwiftUploadObject(obj, options=options) for obj in objs]
        	# Schedule uploads on the SwiftService thread pool and iterate over the results
        	for result in swift.upload(container, objs):
            		if result['success']:
               			if 'object' in result:
                   			print("Successfully uploaded %s." %result['object'])
                		elif 'for_object' in result:
                    			print('%s segment %s' % (result['for_object'],result['segment_index']))
            		else:
                		error = result['error']
                		if result['action'] == "create_container":
                    			print('Warning: failed to create container '"'%s'%s", container, error)
                		elif result['action'] == "upload_object":
                    			print("Failed to upload object %s to container %s: %s" %(container, result['object'], error))
                		else:
                    			print("%s" % error)
    	except SwiftError as e:
		print("SwiftError: %s" %e)
