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
    parser.add_argument('-gf', '--Get-Filenames',dest='gf',action='store_true',default=False,help="Runs the filename harvesting subprocess. This should really only be done once")
    parser.add_argument('-gc', '--Get-Checksums',dest='gc',action='store_true',default=False,help="Runs the checksum harvesting subcprocess. This should really only be done once")
    parser.add_argument('-vc', '--Validate-Checksums',dest='vc',action='store_true',default=False,help="Runs the checksum validation subcprocess. This should be run on a regular basis")
    parser.add_argument('-fa', '--File-Audit',dest='fa',action='store_true',default=False,help="Runs a file-level audio subcprocess. This is more detailed than the auto-audio, which only checks that the Unique ID folders exist. This checks that files exist as well")
    parser.add_argument('-ad', '--Auto-Deaccession',dest='ad',action='store_true',default=False,help="Runs the auto-deaccession subcprocess. This moves all records marked \"Not in Library\" to a _Trash folder. This should be run on a regular basis")
    parser.add_argument('-f', '--Find',dest='f',action='store',help="Runs the find subcprocess. This returns the path of whatever record is searched for")
    args = parser.parse_args()

    if args.d:
        log_level=logging.DEBUG
    else:
        log_level=logging.INFO

    levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]     #The default verbosity level for stdout is CRITICAL
    verbose_level = levels[min(len(levels)-1,args.verbose)]

    logDir = os.getcwd()               # The log will be created at the working directory
    logName = 'recordMaintenance_' + datetime.today().strftime('%Y-%m-%d')  # The script will be named log.log
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

    #Perform a record-level audit. Quit upon failure
    if not recordAudit(airtable, drive_name):
        quit()

    #perform a file-level audit.
    if args.fa:
        fileAudit(airtable, drive_name)

    #Harvest filenames
    if args.gf:
        getFilenames(airtable, drive_name)

    #Harvest checksums
    if args.gc:
        getChecksums(airtable, drive_name)

    #Validate checksums
    if args.vc:
        validateChecksums(airtable, drive_name)

    #Perform audio-deaccession
    if args.ad:
        autoDeaccession(airtable, drive_name)

    #Perform find subcprocess
    if args.f:
        findRecord(args.f, drive_name)

    logging.critical('========Script Complete========')

## End of main function


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
            if record['fields']['In Library'] == "Yes":     #only process records that are in the library
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

def fileAudit(airtable, drive_name):
    print('Performing a file-level audit')
    logging.info('Performing a file-level audit')
    missing_file_counter = 0
    pages = airtable.get_iter()
    for page in pages:
        for record in page:
            if record['fields']['In Library'] == "Yes":     #only process records that are in the library
                record_id = record['id']
                UID = record['fields']['Unique ID']
                try:                                        #checks to see if record has an entry in the File Name field. This will only process empty file names, so as not to overwrite
                    airtable_filename = record['fields']['File Name']
                except Exception as e:
                    logging.info('Updating filename for record %s' % UID)
                try:                                        #Need to have an try/except here because airtable errors if the field is empty. This is in case there is no Group
                    group = record['fields']['Group']
                except Exception as e:
                    group = ""
                if group == "":                             #In case there is no Group, we don't want an extra slash
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
                    if airtable_filename != files_list[0]:
                        missing_file_counter += 1
                        logging.error('Filename Mismatch for record %s. Please fix this before continuing' % UID)
                elif len(files_list) == 0:
                    logging.error('No files found in %s' % UID)
                    missing_file_counter += 1
                else:
                    if airtable_filename != files_list[0]:
                        missing_file_counter += 1
                        logging.error('Filename Mismatch for record %s. Please fix this before continuing' % UID)

    logging.info('File-level audit complete, %i errors found.' % missing_file_counter)
    return

def getFilenames(airtable, drive_name):
    #This section harvests file names and puts them in Airtable's File Name field
    #For now it will only get the first filename, and warns if there is more than one file in the folder
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
                    airtable_filename = record['fields']['File Name']
                    continue
                except Exception as e:
                    logging.info('Updating filename for record %s' % UID)
                try:                                        #Need to have an try/except here because airtable errors if the field is empty. This is in case there is no Group
                    group = record['fields']['Group']
                except Exception as e:
                    group = ""
                if group == "":                             #In case there is no Group, we don't want an extra slash
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
    return

def validateChecksums(airtable, drive_name):
    #This section validates file checksums and updates the "last validated date" field
    #For now it will only get the first filename, and warns if there is more than one file in the folder
    print('Validating Checksums and updating airtable')
    logging.info('Validating Checksums and updating airtable')
    update_counter = 0
    checksum_error_counter = 0
    checksum_validate_counter = 0
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
                try:                                        #Need to have an try/except here because airtable errors if the field is empty. This is in case there is no Group
                    group = record['fields']['Group']
                except Exception as e:
                    group = ""
                if group == "":                             #In case there is no Group, we don't want an extra slash
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
                        checksum_validate_counter += 1
                    else:
                        logging.error('Checksum validation failed for record %s' % UID)
                        update_dict = {'Checksum Valid': 'No', 'Last Checksum Validated Date': datetime.today().strftime('%Y-%m-%d')}
                        checksum_error_counter += 1
                elif len(files_list) == 0:
                    logging.error('No files found in %s' % UID)
                    #update_dict = {'Checksum': 'NO FILE FOUND'}                    #Not to self, need better fail mode here
                else:
                    file_checksum = generateHash(os.path.join(path,files_list[0]))
                    if file_checksum == airtable_checksum:
                        logging.info('Checksum validation succesful for record %s' % UID)
                        update_dict = {'Checksum Valid': 'Yes', 'Last Checksum Validated Date': datetime.today().strftime('%Y-%m-%d')}
                        checksum_validate_counter += 1
                    else:
                        logging.error('Checksum validation failed for record %s' % UID)
                        update_dict = {'Checksum Valid': 'No', 'Last Checksum Validated Date': datetime.today().strftime('%Y-%m-%d')}
                        checksum_error_counter += 1

                #THIS IS THE IMPORTANT BIT WHERE WE UPDATE THE TABLE!
                try:
                    airtable.update(record_id, update_dict)
                    logging.info('Succesfully updated checksum validation date for record %s ' % UID)
                    update_counter += 1
                except Exception as e:
                    logging.error('Could not update checksum validation for record %s' % UID)
                    checksum_error_counter += 1
    logging.info('Checksum Validation complete. %i records succesfully validated, %i Airtable records updated, %i errors encountered. ' % (checksum_validate_counter, update_counter, checksum_error_counter))
    return

def autoDeaccession(airtable, drive_name):
    print('Performing auto-deaccession')
    logging.info('Performing auto-deaccession')
    deaccession_errors = 0
    deaccession_success = 0
    update_counter = 0
    pages = airtable.get_iter()
    trash_path = os.path.join('/Volumes', drive_name, "_Trash")
    if os.path.isdir(trash_path):
        logging.info('Trash folder already exists')
    else:
        os.makedirs(trash_path, exist_ok=False)
        logging.info('New trash folder created')
    for page in pages:
        for record in page:
            if record['fields']['On Drive'] == "Yes":           #only process records that are marked as being on the drive
                if record['fields']['In Library'] == "No":      #We want to find files that are marked as not in the library, so we can remove them from the drive
                    record_id = record['id']
                    UID = record['fields']['Unique ID']
                    try:                                        #Need to have an try/except here because airtable errors if the field is empty. This is in case there is no Group
                        group = record['fields']['Group']
                    except Exception as e:
                        group = ""
                    if group == "":                             #In case there is no Group, we don't want an extra slash
                        path = os.path.join('/Volumes', drive_name, UID)    #will need to fix this to make it cross platform eventually
                    else:
                        path = os.path.join('/Volumes', drive_name, group, UID)    #will need to fix this to make it cross platform eventually
                    if os.path.isdir(path):
                        logging.info('Deaccessioning record %s' % UID)
                        update_dict = {'On Drive': "No"}
                        shutil.move(path,trash_path)
                        deaccession_success += 1
                        #THIS IS THE IMPORTANT BIT WHERE WE UPDATE THE TABLE!
                        try:
                            airtable.update(record_id, update_dict)
                            logging.info('Succesfully set On Drive to No for record %s ' % UID)
                            update_counter += 1
                        except Exception as e:
                            logging.error('Could not set On Drive to No for record %s' % UID)
                            deaccession_errors += 1
                    else:
                        logging.error('Could not find record %s. Ensure that file exists in proper location before running auto-deaccession' % UID)
                        deaccession_errors += 1


    logging.info('Auto deaccession complete. %i records succesfully deaccessioned, %i Airtable records updated, %i errors encountered.' % (deaccession_success, update_counter, deaccession_errors))
    return


def getChecksums(airtable, drive_name):
    #This section harvests file checksums and puts them in Airtable's Checksum field
    #For now it will only get the first filename, and warns if there is more than one file in the folder
    print('Harvesting Checksums and updating airtable')
    logging.info('Harvesting Checksums and updating airtable')
    update_counter = 0
    checksum_counter = 0
    warning_counter = 0
    error_counter = 0
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
                try:                                        #checks to see if record has an entry in the Checksum field. This will only process files with no checksum already, so as not to overwrite
                    airtable_filename = record['fields']['File Name']
                except Exception as e:
                    logging.warning('No File Name in Airtable record for %s. Skipping for now, please run File Name harvesting.' % UID)
                    warning_counter =+ 1
                    continue
                try:                                        #Need to have an try/except here because airtable errors if the field is empty. This is in case there is no Group
                    group = record['fields']['Group']
                except Exception as e:
                    group = ""
                if group == "":                             #In case there is no Group, we don't want an extra slash
                    file_path = os.path.join('/Volumes', drive_name, UID, airtable_filename)    #will need to fix this to make it cross platform eventually
                else:
                    file_path = os.path.join('/Volumes', drive_name, group, UID, airtable_filename)    #will need to fix this to make it cross platform eventually
                try:
                    checksum = generateHash(file_path)
                    update_dict = {'Checksum': checksum}
                    checksum_counter += 1
                except Exception as e:
                    logging.error('Could not gather checksums for record %s. Check that filename is correct' % UID)
                    error_counter += 1
                    continue

                #THIS IS THE IMPORTANT BIT WHERE WE UPDATE THE TABLE!
                try:
                    airtable.update(record_id, update_dict)
                    logging.info('Succesfully updated checksum for record %s ' % UID)
                    update_counter += 1
                except Exception as e:
                    logging.error('Could not update checksums for record %s' % UID)
    logging.info('Checksum harvest complete. %i checksums generated, %i Airtable records updated, %i warnings encountered, %i errors encountered.' % (checksum_counter, update_counter, warning_counter, error_counter))
    return

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
