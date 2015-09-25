
import urllib
import urllib2
import json
import os, sys, time
from urllib2 import HTTPError

#TODO: Check the list of files JSON for recent files

parent_dir = '/Users/dhara/Canvas/'
website = 'https://canvas.instructure.com'
courses_api = '/api/v1/courses'
access_token = 'access_token=12~NWhDT8CUvB14Jgomds2PG21HONDiQrqWb1yMX8HtNsh1OrmWXiGYNbWBgXOo47Ic'

# Fetch the course details
courses_url = website + courses_api + '?' + access_token
response = urllib2.urlopen(courses_url).read()
courses = json.loads(response)              # Parse the JSON response
for course in courses:
    # Create course folders
    course_name = course['name'].split()    # Splitting the name to make it simple
    #TODO: generic course name
    course_dir = parent_dir + course_name[1]
    if not os.path.exists(course_dir):
        print 'Creating ', course_dir
        os.makedirs(course_dir)
    course_id = course['id']

    # Create sub-folders
    folder_url = website + courses_api + '/' + str(course_id) +'/folders?'+ access_token
    try:
        folder_response = urllib2.urlopen(folder_url).read()
        folders = json.loads(folder_response)

        folder_dict = {}
        # Create Sub-folders
        for folder in folders:
            # Creating a dict to store folder name as file object has only folder ID
            folder_name = folder['name']
            folder_dict[folder['id']] = folder_name
            folder_dir = course_dir + '/' + folder_name
            if not os.path.exists(folder_dir):
                print 'Creating', folder_dir
                os.makedirs(folder_dir)

        # Downloading files in the respective folders
        try:
            files_url = website + courses_api + '/' + str(course_id) + '/files?' + access_token
            files_response = urllib2.urlopen(files_url).read()
            # Parsing the JSON response
            files = json.loads(files_response)
            for file in files:
                # Deciding file location
                file_location = course_dir + '/' + folder_dict[file['folder_id']] + '/'
                file_url = file['url']
                file_name = file['filename']
                file_path = file_location + file_name
                print 'Downloading ', file_name
                #TODO: time.ctime(os.path.getmtime(file)) != file['updated_at']
                if not os.path.isfile(file_path):
                    urllib.urlretrieve(file_url, file_path)
        except HTTPError as fileE:
            print 'No files for course', course_name[1]
    except HTTPError as folderE:
        print 'No folders for course', course_name[1]