#!/usr/bin/env python
import sys
from swiftclient.service import SwiftService, SwiftCopyObject, SwiftError

# function needed for obtaining the list of objects in container
def isfiletype(x, filetype):
    return (x["name"].lower().endswith(filetype))

# first argument is the original container name, second is the destination (new) container
def swiftcopy_function(original_container, dest_container):

    # now obtain a list of all of the objects to copy to the new container (this grabs all of the objects in container)
    object_list = []
    with SwiftService() as swift:
        try:
            list_parts_gen = swift.list(container=original_container)
            for page in list_parts_gen:
                if page["success"]:
                    for item in page["listing"]:
                        if isfiletype(item, ''):
                            size = int(item["bytes"])
                            name = item["name"]
                            etag = item["hash"]
                            object_list.append(name)
                else: 
                    raise page["error"]
        except SwiftError as e:
            print("SwiftError: %s" %e)

    # using this list, copy the objects to destination container
    with SwiftService() as swift:
        try:
            for i in swift.copy(original_container, object_list, {"destination": "/" + dest_container}):
                if i["success"]:
                    if i["action"] == "copy_object":
                        print(
                            "object %s copied from /%s/%s" %
                            (i["destination"], i["container"], i["object"])
                        )
                    if i["action"] == "create_container":
                        print(
                            "container %s created" % i["container"]
                        )
                else:
                    if "error" in i and isinstance(i["error"], Exception):
                        raise i["error"]
        except SwiftError as e:
            print("SwiftError: %s" %e)

if __name__ == "__main__":
    # if this script is being called by itself, need to specify the two containers to input into function
    original_container = sys.argv[1]
    dest_container = sys.argv[2]
    swiftcopy_function(original_container, dest_container)
