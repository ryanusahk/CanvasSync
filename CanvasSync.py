import urllib
import urllib2
import json
import os, sys, time
from urllib2 import HTTPError
import os.path

home = os.path.expanduser("~")

website = 'https://bcourses.berkeley.edu'
courses_api = '/api/v1/courses'
settings_file = 'sync_settings.settings'
readout_mode = len(sys.argv) > 1

course_to_folder = {}

if not os.path.isfile(settings_file):
    print 'Welcome to the setup!'
    course_to_folder['ACCESS_TOKEN__'] = raw_input('Paste your access token: ')
    courses_url = website + courses_api + '?per_page=100&access_token=' + course_to_folder['ACCESS_TOKEN__']
    response = urllib2.urlopen(courses_url).read()
    courses = json.loads(response) 

    print 'Where do you want to sync to? Make sure the directory already exists.'
    response = raw_input('Enter the directory relative to ~ (start with /): ')

    if response[0] != '/':
        response = '/' + response
    if response[-1] != '/':
        response = response + '/'
    course_to_folder['directory__'] = response

    course_to_folder['directory__']
    print 'Enter a folder name for each class, or a . to not sync the class'
    for course in courses:
        response = raw_input(course['name'] + '\t')

        if response != '.':
            course_to_folder[course['name']] = response

    open(settings_file, 'w').write(json.dumps(course_to_folder))


course_to_folder = json.loads(open(settings_file, 'r').read())
access_token = 'access_token=' + course_to_folder['ACCESS_TOKEN__']
parent_dir = home + course_to_folder['directory__']

# Fetch the course details
courses_url = website + courses_api + '?per_page=100&' + access_token
response = urllib2.urlopen(courses_url).read()
courses = json.loads(response)              # Parse the JSON response


for course in courses:
    # Create course folders
    if 'name' not in course or course['name'] not in course_to_folder:
        continue
    course_name = course_to_folder[course['name']]    # Splitting the name to make it simple
    print 'Syncing ' + course_name
    course_dir = parent_dir + course_name
    if not os.path.exists(course_dir):
        print 'Creating ', course_dir
        os.makedirs(course_dir)
    course_id = course['id']

    # Create sub-folders
    folder_url = website + courses_api + '/' + str(course_id) +'/folders?per_page=100&'+ access_token
    try:
        folder_response = urllib2.urlopen(folder_url).read()
        folders = json.loads(folder_response)
        folder_dict = {}
        # Create Sub-folders
        for folder in folders:
            # Creating a dict to store folder name as file object has only folder ID
            folder_name = folder['full_name']
            folder_dict[folder['id']] = folder_name
            folder_dir = course_dir + '/' + folder_name
            folder_dir = folder_dir.replace('/course files', '')
            if not os.path.exists(folder_dir):
                print 'Creating', folder_dir
                os.makedirs(folder_dir)

        # Downloading files in the respective folders
        try:
            p_num = 1
            while True:
                files_url = website + courses_api + '/' + str(course_id) + '/files?page=' + str(p_num) + '&per_page=20&' + access_token
                files_response = urllib2.urlopen(files_url).read()
                if files_response == '[]':
                    break
                # Parsing the JSON response
                files = json.loads(files_response)
                for file in files:
                    # Deciding file location
                    file_location = course_dir + '/' + folder_dict[file['folder_id']] + '/'
                    file_url = file['url']
                    file_name = file['display_name']
                    file_path = file_location + urllib.unquote(file_name).replace('+', ' ')
                    file_path = file_path.replace('/course files', '')

                    if not os.path.isfile(file_path):
                        print 'Downloading ', file_path.split('/')[-1]
                        urllib.urlretrieve(file_url, file_path)
                    elif readout_mode:
                        print 'Skipping    ', file_path.split('/')[-1]                    
                p_num += 1
        except HTTPError as fileE:
            print 'No files for course', course_name
    except HTTPError as folderE:
        print 'No folders for course', course_name
print 'Sync Complete!'