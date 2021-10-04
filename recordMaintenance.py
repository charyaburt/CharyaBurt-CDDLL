#!/usr/local/bin/python3


'''
just getting started
'''
import logging          # This loads the "logging" module, which handles logging very simply
import os               # This loads the "os" module, useful for dealing with filepaths
import tempfile         # This loads the "tempfile" module, a nice cross-platform way to deal with temp directories
import subprocess
import sys
import platform
import argparse         # This loads the "argparse" module, used for parsing input arguments which allows us to have a verbose mode
import config
import hashlib
from datetime import datetime   # This lades the datetime module, used for getting dates and timestamps
from pprint import pprint
from airtable import Airtable

def main():

### Collect input arguments from the user. For now we just use this to run the script in verbose and debug mode
    parser = argparse.ArgumentParser(description="This is a simple testing script for Airtable / Python stuff with logging")
    parser.add_argument('-v', '--verbose', action='count', default=0,help="Defines verbose level for standard out (stdout). v = warning, vv = info, vvv = debug")
    parser.add_argument('-d', '--Debug',dest='d',action='store_true',default=False,help="turns on Debug mode, which send all DEBUG level (and below) messages to the log. By default logging is set to INFO level")
    parser.add_argument('-gf', '--Get-Filenames',dest='gf',action='store_true',default=False,help="Runs the filename harvesting subprocess. This should really only be done once")
    parser.add_argument('-gc', '--Get-Checksums',dest='gc',action='store_true',default=False,help="Runs the checksum harvesting subcprocess. This should really only be done once")
    parser.add_argument('-vc', '--Validate-Checksums',dest='vc',action='store_true',default=False,help="Runs the checksum validation subcprocess. This should be run on a regular basis")
    args = parser.parse_args()

    if args.d:
        log_level=logging.DEBUG
    else:
        log_level=logging.INFO

    levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]     #The default verbosity level for stdout is CRITICAL
    verbose_level = levels[min(len(levels)-1,args.verbose)]

    logDir = os.getcwd()               # The log will be created at the working directory
    logName = 'simplyPyAt'                                 # The script will be named log.log
    logPath = logDir + "/" + logName + ".log"         # This creates the full log path based off the selected options
    LOG_FORMAT = '%(asctime)s - %(levelname)s: %(message)s' #Timestamp - Loglevel: Message
    logger = logging.getLogger()
    logging.basicConfig(filename=logPath, encoding='utf-8', level=log_level, format=LOG_FORMAT)    # Creates the Log
    STDOUT_FORMAT = '%(message)s'                             #Message
    logging_handler_out = logging.StreamHandler(sys.stdout)
    logging_handler_out.setLevel(verbose_level)
    logging_handler_out.setFormatter(logging.Formatter(STDOUT_FORMAT))
    logger.addHandler(logging_handler_out)

    logging.critical('========Starting Script========')


#The following section is a cross-platform way to open the log
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', logPath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(logPath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))

###     Now that the log is setup we can send some messages to it!

    #logging.debug('This is a debug message')
    #logging.info('This is a standard message')
    #logging.warning('This is a warning')
    #logging.error('This is an error')
    #logging.critical('This is a critical message')


#Need to test for dependencies here. Config.py as well as libraries

    base_key=config.BASE_ID         #This stuff comes from the config.py file. Very important!
    api_key=config.API_KEY
    drive_name=config.DRIVE_NAME
    table_name = "Videos"

    airtable = Airtable(base_key, table_name, api_key)
    pages = airtable.get_iter()

    #This performs a quick audit and will exit if it finds the drive out of sync with the airtable
    logging.info('Performing Record Audit between Airtable and Drive titled: %s' % drive_name)
    missing_record_count = 0
    for page in pages:
        for record in page:
            if record['fields']['In Library'] == "Yes":     #only process records that are in the library
                UID = record['fields']['Unique ID']
                try:                                        #Need to have an try/except here because airtable errors if the field is empty. This is in case there is no Grouping
                    group = record['fields']['Grouping']
                except Exception as e:
                    group = ""
                if group == "":                             #In case there is no grouping, we don't want an extra slash
                    path = os.path.join('/Volumes', drive_name, UID)    #will need to fix this to make it cross platform eventually
                else:
                    path = os.path.join('/Volumes', drive_name, group, UID)    #will need to fix this to make it cross platform eventually
                if not os.path.isdir(path):
                    logging.error('Could not find record %s' % UID)
                    missing_record_count += 1
    if missing_record_count > 0:
        print('ERROR: This script has found at least one missing record. Please consult the log and fix this problem before continuing')
        logging.error('This script has found at least one missing record. Please fix this before continuing')
        quit()

    print('Archive is clean, moving on')
    logging.info('Archive is clean, moving on')

    #This section harvests file names and puts them in Airtable's File Name field
    #For now it will only get the first filename, and warns if there is more than one file in the folder
    if args.gf:
        print('Harvesting File names and updating airtable')
        logging.info('Harvesting File names and updating airtable')
        update_counter = 0
        pages = airtable.get_iter()
        for page in pages:
            for record in page:
                if record['fields']['In Library'] == "Yes":     #only process records that are in the library
                    record_id = record['id']
                    UID = record['fields']['Unique ID']
                    try:                                        #checks to see if record has an entry in the File Name field. This will only process empty file names, so as not to overwrite
                        group = record['fields']['File Name']
                        continue
                    except Exception as e:
                        logging.info('Updating filename for record %s' % UID)
                    try:                                        #Need to have an try/except here because airtable errors if the field is empty. This is in case there is no Grouping
                        group = record['fields']['Grouping']
                    except Exception as e:
                        group = ""
                    if group == "":                             #In case there is no grouping, we don't want an extra slash
                        path = os.path.join('/Volumes', drive_name, UID)    #will need to fix this to make it cross platform eventually
                    else:
                        path = os.path.join('/Volumes', drive_name, group, UID)    #will need to fix this to make it cross platform eventually
                    files_list = []
                    for f in os.listdir(path):
                        if os.path.isfile(os.path.join(path, f)):
                            if not f.startswith('.'):     #avoid hidden files
                                files_list.append(f)
                    files_list.sort()                      #sort the list so it'll always pick the first file.
                    if len(files_list) > 1:
                        logging.warning('Multiple files found in ' + UID + ', using ' + files_list[0])
                        update_dict = {'File Name': files_list[0]}
                    elif len(files_list) == 0:
                        logging.error('No files found in %s' % UID)
                        update_dict = {'File Name': 'NO FILE FOUND'}
                    else:
                        update_dict = {'File Name': files_list[0]}

                    #THIS IS THE IMPORTANT BIT WHERE WE UPDATE THE TABLE!
                    try:
                        airtable.update(record_id, update_dict)
                        logging.info('Succesfully updated filename for record %s ' % UID)
                        update_counter += 1
                    except Exception as e:
                        logging.error('Could not update filename for record %s' % UID)
        logging.info('Finished updating filenames for %i records' % update_counter)

    #This section harvests file checksums and puts them in Airtable's Checksum field
    #For now it will only get the first filename, and warns if there is more than one file in the folder
    if args.gc:
        print('Harvesting Checksums and updating airtable')
        logging.info('Harvesting Checksums and updating airtable')
        update_counter = 0
        pages = airtable.get_iter()
        for page in pages:
            for record in page:
                if record['fields']['In Library'] == "Yes":     #only process records that are in the library
                    record_id = record['id']
                    UID = record['fields']['Unique ID']
                    try:                                        #checks to see if record has an entry in the Checksum field. This will only process files with no checksum already, so as not to overwrite
                        airtable_checksum = record['fields']['Checksum']
                        continue
                    except Exception as e:
                        logging.info('Updating Checksum for record %s' % UID)
                    try:                                        #Need to have an try/except here because airtable errors if the field is empty. This is in case there is no Grouping
                        group = record['fields']['Grouping']
                    except Exception as e:
                        group = ""
                    if group == "":                             #In case there is no grouping, we don't want an extra slash
                        path = os.path.join('/Volumes', drive_name, UID)    #will need to fix this to make it cross platform eventually
                    else:
                        path = os.path.join('/Volumes', drive_name, group, UID)    #will need to fix this to make it cross platform eventually
                    files_list = []
                    for f in os.listdir(path):
                        if os.path.isfile(os.path.join(path, f)):
                            if not f.startswith('.'):     #avoid hidden files
                                files_list.append(f)
                    files_list.sort()                      #sort the list so it'll always pick the first file.
                    if len(files_list) > 1:
                        logging.warning('Multiple files found in ' + UID + ', using ' + files_list[0])
                        checksum = generateHash(os.path.join(path,files_list[0]))
                        update_dict = {'Checksum': checksum}
                    elif len(files_list) == 0:
                        logging.error('No files found in %s' % UID)
                        update_dict = {'Checksum': 'NO FILE FOUND'}
                    else:
                        checksum = generateHash(os.path.join(path,files_list[0]))
                        update_dict = {'Checksum': checksum}

                    #THIS IS THE IMPORTANT BIT WHERE WE UPDATE THE TABLE!
                    try:
                        airtable.update(record_id, update_dict)
                        logging.info('Succesfully updated checksum for record %s ' % UID)
                        update_counter += 1
                    except Exception as e:
                        logging.error('Could not update checksums for record %s' % UID)
        logging.info('Finished updating checksums for %i records' % update_counter)

    #This section validates file checksums and updates the "last validated date" field
    #For now it will only get the first filename, and warns if there is more than one file in the folder
    if args.vc:
        print('Validating Checksums and updating airtable')
        logging.info('Validating Checksums and updating airtable')
        update_counter = 0
        pages = airtable.get_iter()
        for page in pages:
            for record in page:
                if record['fields']['In Library'] == "Yes":     #only process records that are in the library
                    record_id = record['id']
                    UID = record['fields']['Unique ID']
                    try:                                        #checks to see if record has an entry in the checksum field. This will only process records with existing checksums
                        airtable_checksum = record['fields']['Checksum']
                    except Exception as e:
                        logging.warning('No Chucksum found for record %s. Skipping validation. Please run checksum creation subprocess to ensure records are up to date.' % UID)
                        continue
                    try:                                        #Need to have an try/except here because airtable errors if the field is empty. This is in case there is no Grouping
                        group = record['fields']['Grouping']
                    except Exception as e:
                        group = ""
                    if group == "":                             #In case there is no grouping, we don't want an extra slash
                        path = os.path.join('/Volumes', drive_name, UID)    #will need to fix this to make it cross platform eventually
                    else:
                        path = os.path.join('/Volumes', drive_name, group, UID)    #will need to fix this to make it cross platform eventually
                    files_list = []
                    for f in os.listdir(path):
                        if os.path.isfile(os.path.join(path, f)):
                            if not f.startswith('.'):     #avoid hidden files
                                files_list.append(f)
                    files_list.sort()                      #sort the list so it'll always pick the first file.
                    if len(files_list) > 1:
                        logging.warning('Multiple files found in ' + UID + ', using ' + files_list[0])
                        file_checksum = generateHash(os.path.join(path,files_list[0]))
                        if file_checksum == airtable_checksum:
                            logging.info('Checksum validation succesful for record %s' % UID)
                            update_dict = {'Checksum Valid': 'Yes', 'Last Checksum Validated Date': datetime.today().strftime('%Y-%m-%d')}
                        else:
                            logging.error('Checksum validation failed for record %s' % UID)
                            update_dict = {'Checksum Valid': 'No', 'Last Checksum Validated Date': datetime.today().strftime('%Y-%m-%d')}
                    elif len(files_list) == 0:
                        logging.error('No files found in %s' % UID)
                        #update_dict = {'Checksum': 'NO FILE FOUND'}                    #Not to self, need better fail mode here
                    else:
                        file_checksum = generateHash(os.path.join(path,files_list[0]))
                        if file_checksum == airtable_checksum:
                            logging.info('Checksum validation succesful for record %s' % UID)
                            update_dict = {'Checksum Valid': 'Yes', 'Last Checksum Validated Date': datetime.today().strftime('%Y-%m-%d')}
                        else:
                            logging.error('Checksum validation failed for record %s' % UID)
                            update_dict = {'Checksum Valid': 'No', 'Last Checksum Validated Date': datetime.today().strftime('%Y-%m-%d')}

                    #THIS IS THE IMPORTANT BIT WHERE WE UPDATE THE TABLE!
                    try:
                        airtable.update(record_id, update_dict)
                        logging.info('Succesfully updated checksum validation date for record %s ' % UID)
                        update_counter += 1
                    except Exception as e:
                        logging.error('Could not update checksum validationd ate for record %s' % UID)
        logging.info('Finished updating checksums for %i records' % update_counter)


    logging.critical('========Script Complete========')


def generateHash(inputFile, blocksize=65536):
    '''
    using a buffer, hash the file
    '''
    md5 = hashlib.md5()

    with open(inputFile, 'rb') as f:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
