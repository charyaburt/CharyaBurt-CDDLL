#!/usr/local/bin/python3

import logging          # This loads the "logging" module, which handles logging very simply
import os               # This loads the "os" module, useful for dealing with filepaths
import tempfile         # This loads the "tempfile" module, a nice cross-platform way to deal with temp directories
import subprocess
import sys
import platform
import argparse         # This loads the "argparse" module, used for parsing input arguments which allows us to have a verbose mode
import config
import hashlib
import shutil           # Needed for auto-deaccsion subprocess
import pathlib             # Needed for find subprocess
from datetime import datetime   # This lades the datetime module, used for getting dates and timestamps
from pprint import pprint
from airtable import Airtable


def main():

### Collect input arguments from the user. For now we just use this to run the script in verbose and debug mode
    parser = argparse.ArgumentParser(description="This is a simple testing script for Airtable / Python stuff with logging")
    parser.add_argument('-v', '--verbose', action='count', default=0,help="Defines verbose level for standard out (stdout). v = warning, vv = info, vvv = debug")
    parser.add_argument('-d', '--Debug',dest='d',action='store_true',default=False,help="turns on Debug mode, which send all DEBUG level (and below) messages to the log. By default logging is set to INFO level")
    parser.add_argument('-r', '--Record',dest='r',action='store',default=None,help="Set the record ID you want to add to the archive")
    parser.add_argument('-f', '--File',dest='f',action='store',default=None,help="Sets the filepath of the file you want to add to the archive")
    args = parser.parse_args()

    if args.d:
        log_level=logging.DEBUG
    else:
        log_level=logging.INFO

    levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]     #The default verbosity level for stdout is CRITICAL
    verbose_level = levels[min(len(levels)-1,args.verbose)]

    logDir = os.getcwd()               # The log will be created at the working directory
    logName = 'addFile_' + datetime.today().strftime('%Y-%m-%d')  # The script will be named log.log
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
    table_name = config.TABLE_NAME

    airtable = Airtable(base_key, table_name, api_key)

    #Checks to see if input arguments have been properly entered
    #Check to see if file argument exists is properly formed
    checkFileArg(args.f)

    #Check to see if record argument exists is properly formed
    checkRecordArg(airtable, drive_name, args.r)

    #Perform a record-level audit. Quit upon failure
    if not recordAudit(airtable, drive_name):
        quit()

    #Add the file to the archive. This involves moving it to the right folder, harvesting the name and the checksum
    addToArchive(airtable, drive_name, args.r, args.f)

    logging.critical('========Script Complete========')

## End of main function

def addToArchive(airtable, drive_name, recordID, file_path):
    # This script collects the checksum and filename info and puts it in airtable, then moves the file to the correct location
    # This part finds the airtable record ID so we can updated the filename and checksum info
    file_name = os.path.basename(file_path)
    pages = airtable.get_iter()
    for page in pages:
        for record in page:
            if record['fields']['Unique ID'] == recordID:     #only process records that are in the library
                record_airtable_id = record['id']
                try:                                        #Need to have an try/except here because airtable errors if the field is empty. This is in case there is no Group
                    record_airtable_group = record['fields']['Group']
                except Exception as e:
                    record_airtable_group = ""

    if record_airtable_group == "":                             #In case there is no Group, we don't want an extra slash
        new_group_path = None
        new_record_path = os.path.join('/Volumes', drive_name, recordID)
        new_file_path = os.path.join('/Volumes', drive_name, recordID, file_name)
    else:
        new_group_path = os.path.join('/Volumes', drive_name, record_airtable_group)
        new_record_path = os.path.join('/Volumes', drive_name, record_airtable_group, recordID)
        new_file_path = os.path.join('/Volumes', drive_name, record_airtable_group, recordID, file_name)

    logging.info('Generating checksum for record ID: %s' % recordID)
    checksum = generateHash(file_path)
    logging.info('Checksum generating completed!')
    checksum_update_dict = {'Checksum': checksum}
    filename_update_dict = {'File Name': file_name}
    on_drive_update_dict = {'On Drive': "Yes"}
    in_library_update_dict = {'In Library': "Yes"}

    #Check to see if group folder exists, if not creates it
    if new_group_path == None:
        logging.info('No group selected for this record. Record folder will exist at the root level of the drive')
    elif os.path.isdir(new_group_path):
        logging.info('Group folder already exists')
    else:
        logging.info('Group folder does not exist. Creating it now')
        os.makedirs(new_group_path, exist_ok=False)
        logging.info('Sucess creating Group folder')

    #Check to see if record folder exists, if not creates it. if it exist and the file is already there it quits because that's not supposed to happen
    if os.path.isdir(new_record_path):
        logging.warning('Record ID Folder Already Exists')
        if os.path.isfile(new_file_path):
            logging.error('File already exists in the archive! Quitting Now')
            logging.critical('========Script Complete========')
            quit()
    else:
        os.makedirs(new_record_path, exist_ok=False)

    #Move the file to the drive
    try:    #doing the move in a try block just in case
        shutil.move(file_path,new_record_path)
        logging.info('Sucess moving file to drive')
    except Exception as e:
        logging.error('Failed to move file to drive. Quitting Now')
        logging.critical('========Script Complete========')
        quit()

    #now that we've succesfully put the file on the drive, let's put the filename and checksum in airtable
    updateRecord(airtable, record_airtable_id, checksum_update_dict, recordID, 'Checksum')
    updateRecord(airtable, record_airtable_id, filename_update_dict, recordID, 'Filename')
    updateRecord(airtable, record_airtable_id, on_drive_update_dict, recordID, 'On Drive')
    updateRecord(airtable, record_airtable_id, in_library_update_dict, recordID, 'In Library')

def updateRecord(airtable, record_airtable_id, update_dict, UID, field_name):
    try:
        airtable.update(record_airtable_id, update_dict)
        logging.info('Succesfully updated %s for Record ID: %s ' % (field_name, UID))
    except Exception as e:
        logging.error('Could not updated %s for record %s' % (field_name, UID))

def checkRecordArg(airtable, drive_name, recordID):
    if recordID is None:
        print('ERROR: You must enter a Record ID to add to the archive using the -r flag')
        logging.error('You must enter a Record ID to add to the archive using the -r flag')
        logging.critical('========Script Complete========')
        quit()
    elif not recordExists(airtable, drive_name, recordID):
        print('ERROR: You must enter a valid Record ID path after the -r flag. Make sure you have already added the selected ID in Airtable before continuing.')
        logging.error('You must enter a valid Record ID path after the -r flag. Make sure you have already added the selected ID in Airtable before continuing')
        logging.critical('========Script Complete========')
        quit()

def checkFileArg(inFile):
    if inFile is None:
        print('ERROR: You must enter a file path to add to the archive using the -f flag')
        logging.error('You must enter a file path to add to the archive using the -f flag')
        logging.critical('========Script Complete========')
        quit()
    elif not os.path.isfile(inFile):
        print('ERROR: You must enter a valid file path after the -f flag')
        logging.error('You must enter a valid file path after the -f flag')
        logging.critical('========Script Complete========')
        quit()

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

def recordAudit(airtable, drive_name):
    #This performs a quick audit and will exit if it finds the drive out of sync with the airtable
    pages = airtable.get_iter()
    logging.info('Performing Record Audit between Airtable and Drive titled: %s' % drive_name)
    missing_record_count = 0
    for page in pages:
        for record in page:
            try:
                in_library = record['fields']['In Library']
            except Exception as e:
                in_library = "Not Found"
            if in_library == "Yes":     #only process records that are in the library
                UID = record['fields']['Unique ID']
                try:                                        #Need to have an try/except here because airtable errors if the field is empty. This is in case there is no Group
                    group = record['fields']['Group']
                except Exception as e:
                    group = ""
                if group == "":                             #In case there is no Group, we don't want an extra slash
                    path = os.path.join('/Volumes', drive_name, UID)    #will need to fix this to make it cross platform eventually
                else:
                    path = os.path.join('/Volumes', drive_name, group, UID)    #will need to fix this to make it cross platform eventually
                if not os.path.isdir(path):
                    logging.error('Could not find record %s' % UID)
                    missing_record_count += 1
    if missing_record_count > 0:
        print('ERROR: This script has found at least one missing record. Please consult the log and fix this problem before continuing')
        logging.error('This script has found at least one missing record. Please fix this before continuing')
        logging.critical('========Script Complete========')
        return False

    print('Record Level Audit completed succesfully')
    logging.info('Record Level Audit completed succesfully')
    return True

def recordExists(airtable, drive_name, recordID):
    #checks to see if the selected record exists in Airtable
    pages = airtable.get_iter()
    logging.info('Checking if record ID %s exists' % recordID)
    for page in pages:
        for record in page:
            if record['fields']['Unique ID'] == recordID:     #only process records that are in the library
                print('Record %s found in Airtable!' % recordID)
                logging.info('Record %s found in Airtable!' % recordID)
                return True
    return False


def findRecord(UID, drive_name):
    # Performs the find subprocess. Returns the full path of the record folder.
    # It will first look for the file in a group, if it can't find it in a group it looks as the root level
    # If it can't find it anywhere it throws an error

    p = pathlib.Path('/Volumes/' + drive_name).glob('**/' + UID)
    files = [x for x in p if x.is_dir()]
    nontrash_Records = []   #making a list of records not in the trash can
    for file in files:
        if '_Trash' not in str(file):
            nontrash_Records.append(file)
    if len(nontrash_Records) == 1:
        #print(str(files[0]))                                            #commented out standard output
        logging.info('Record %s found at: %s' % (UID, str(nontrash_Records[0])))
    elif len(nontrash_Records) == 0:
        #print('ERROR: Record %s not found' % (UID))                     #commented out standard output
        logging.error('Record %s not found' % (UID))
    elif len(nontrash_Records) > 1:
        #print('ERROR: Multiple versions of record %s found at the following locations:' % (UID))    #commented out standard output
        logging.error('Multiple versions of %s found at the following locations:' % (UID))
        for file in nontrash_Records:
            #print('%s' % (str(file)))                                   #commented out standard output
            logging.error('%s' % (str(file)))



# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
