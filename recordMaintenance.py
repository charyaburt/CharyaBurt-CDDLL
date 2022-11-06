#!/usr/bin/env python3

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
import pathlib          # Needed for find subprocess
import vimeo            # Needed for uploading files to Vimeo
from datetime import datetime   # This lades the datetime module, used for getting dates and timestamps
from pprint import pprint
from airtable import Airtable


def main():

### Collect input arguments from the user. For now we just use this to run the script in verbose and debug mode
    parser = argparse.ArgumentParser(description="This is a simple testing script for Airtable / Python stuff with logging")
    parser.add_argument('-v', '--verbose', action='count', default=0,help="Defines verbose level for standard out (stdout). v = warning, vv = info, vvv = debug")
    parser.add_argument('-d', '--Debug',dest='d',action='store_true',default=False,help="turns on Debug mode, which send all DEBUG level (and below) messages to the log. By default logging is set to INFO level")
    parser.add_argument('-sa', '--Skip-Audit',dest='sa',action='store_true',default=False,help="Skips drive, airtable, and file audit at beginning of script")
    parser.add_argument('-gc', '--Get-Checksums',dest='gc',action='store_true',default=False,help="Runs the checksum harvesting subcprocess. This should really only be done once")
    parser.add_argument('-vc', '--Validate-Checksums',dest='vc',action='store_true',default=False,help="Runs the checksum validation subcprocess. This should be run on a regular basis")
    parser.add_argument('-da', '--Deaccession',dest='da',action='store_true',default=False,help="Runs the Deaccession subcprocess. This moves all records marked \"Not in Library\" to a _Trash folder. This should be run on a regular basis")
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

    # Setup Airtable Credentials for API

    #base_key=config.BASE_ID         #This stuff comes from the config.py file. Very important!
    #api_key=config.API_KEY
    drive_name=config.DRIVE_NAME
    #table_name = config.TABLE_NAME #don't need this anymore. there's more tables so we need to ask for the info better.

    #airtable = Airtable(base_key, table_name, api_key)

    #Perform audio-deaccession This needs to run first to keep everything else up to date
    if args.da:
        deaccession()

    #skip audits if run with -sa flag
    if not args.sa:

        #Perform a drive audit. Quit upon failure
        drive_audit = driveAudit()

        #perform an airtable audit.
        airtable_audit = airtableAudit()

        #perform a file-level audit.
        file_audit = fileAudit()

        #quit if either the airtable audio or drive audio return False
        if drive_audit and airtable_audit and file_audit:
            pass
        else:
            if not drive_audit:
                logging.error('Drive audit failed. Please fix this before continuing.')
            if not airtable_audit:
                logging.error('Airtable audit failed. Please fix this before continuing.')
            if not file_audit:
                logging.error('File audit failed. Please fix this before continuing.')
            logging.critical('========Script Complete========')
            quit()


    #Harvest checksums for any non-album records missing a checksum
    if args.gc:
        getChecksums()

    #Validate checksums
    if args.vc:
        validateChecksums()



    #Perform find subcprocess
    #Depracated
    #if args.f:
    #    findRecord(args.f, drive_name)

    #needs to be moved to a vimeo maintenance script
    #Perform Download Vimeo subprocess
    #if args.dv:
    #    downloadVimeo(airtable, drive_name)

    #needs to be moved to a vimeo maintenance script
    #Perform Upload Vimeo subprocess
#    if args.uv > 0:

#        v = vimeo.VimeoClient(
#        token=config.YOUR_ACCESS_TOKEN,
#        key=config.YOUR_CLIENT_ID,
#        secret=config.YOUR_CLIENT_SECRET
#        )

        ## Make the request to the server for the "/me" endpoint.
#        about_me = v.get('/me')

        ## Make sure we got back a successful response.
#        assert about_me.status_code == 200

#        uploadVimeo(airtable, v, drive_name, args.uv)
        # Setup Vimeo Credentials for API_KEY

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

def getAirtablePages(table_name):
    #takes table name, returns pages.
    #BASE_ID and API_KEY come from config.py file.
    airtable = Airtable(config.BASE_ID, table_name, config.API_KEY)
    pages = airtable.get_iter()
    return pages

def driveAudit():
    #This performs a quick drive audit, checking to see if drive contains every record labeled as "in library" in airtable
    #TODO -> harvest "on drive" info from related file record for more accurate maintenance
    #TODO -> drill down to filename and checksum name to see if that info needs to be harvested
    drive_name = config.DRIVE_NAME
    pages = getAirtablePages("Records")
    logging.info('Performing record level drive audit. Checking Drive against Airtable, using Drive titled: %s' % drive_name)
    missing_from_drive_count = 0
    correct_on_drive_count = 0
    warning_count = 0
    no_status = 0
    for page in pages:
        for record in page:
            RID = record['fields'][config.RECORD_NUMBER]
            try:
                record_status = record['fields'][config.RECORD_STATUS]
            except Exception as e:
                record_status = "None"  #it is worth noting and telling the user if a file doesn't have a status
            if record_status != config.RECORD_DEACCESS_FLAG:     #only process records that are in the library
                path = os.path.join('/Volumes', drive_name, RID)    #will need to fix this to make it cross platform eventually
                if not os.path.isdir(path):
                    logging.error('Could not find folder for record %s on drive named %s' % (RID, drive_name))
                    missing_from_drive_count += 1
                else:
                    correct_on_drive_count += 1
                if record_status == "None":
                    no_status += 1
                    logging.warning('Record %s has no status. Please enter a status for this record.' % RID)
            else:
                path = os.path.join('/Volumes', drive_name, RID)    #will need to fix this to make it cross platform eventually
                if os.path.isdir(path):
                    logging.error('Deaccessioned record %s was found on drive %s' % (RID, drive_name))

    if no_status > 1:
        logging.warning('Record level drive audit has identified %i record(s) without a status. Please fix this before continuing.' % no_status)
    if missing_from_drive_count > 0:
        print('ERROR: Record level drive audit has found %i missing record(s). Please consult the log and fix this problem before continuing. %i record(s) were succesfully located' % (missing_from_drive_count, correct_on_drive_count))
        logging.error('Record level drive audit has identified %i missing record(s). Please fix this before continuing.' % missing_from_drive_count)
        logging.info('%i record(s) were succesfully located' % correct_on_drive_count)
#        if not_added_record_count > 0:
#            logging.warning('There are records in the Airtable that have not yet been added onto the drive. This should be addressed as soon as possible')
#            warning_count += 1
        return False
    else:
#        if not_added_record_count > 0:3
#            logging.warning('There are records in the Airtable that have not yet been added onto the drive. This should be addressed as soon as possible')
#            warning_count += 1
#        if warning_count == 0:
        print('Record level drive audit completed. %i record(s) were succesfully located' % correct_on_drive_count)
        logging.info('Record level drive audit completed succesfully. %i record(s) were succesfully located' % correct_on_drive_count)
#        else:
#            print('Record Level Audit completed succesfully, however '+ str(warning_count) +' warnings were encountered. Please read the log for details')
#            logging.info('Record Level Audit completed succesfully, however %i warnings were encountered. Please read the log for details', warning_count)
        return True

def airtableAudit():
    #This performs a quick drive audit, checking to see if drive contains every reord labeled as "in library" in airtableAudit
    drive_name = config.DRIVE_NAME
    logging.info('Performing Record level Airtable audit checking Airtable against Drive titled: %s.' % drive_name)
    in_airtable_and_in_library = 0
    in_airtable_not_in_library = 0
    missing_from_airtable_count = 0

    record_dict = {}
    pages = getAirtablePages("Records")
    for page in pages:
        for record in page:
            RID = record['fields'][config.RECORD_NUMBER]
            try:
                record_status = record['fields'][config.RECORD_STATUS]
            except Exception as e:
                record_status = "None"
            record_dict.update({RID: record_status})

    drive_path = os.path.join('/Volumes', drive_name)
    for item in os.listdir(drive_path):
        if os.path.isdir(os.path.join(drive_path, item)):
            if item.startswith("CB"):
                found_in_airtable = False       # initiate found boolean as false
                if item in record_dict:
                    if record_dict.get(item) == config.RECORD_DEACCESS_FLAG:
                        in_airtable_not_in_library += 1
                        logging.error('Record %s was found in Airtable but was labeled "Not In Library" despite being on the drive' % item)
                    else:
                        in_airtable_and_in_library += 1
                        #logging.debug('Record %s was found in Airtable' % item)
                else:
                    logging.error('Could not find record %s on the Airtable' % item)
                    missing_from_airtable_count += 1
    if missing_from_airtable_count > 0:
        print('ERROR: This script has found %i record(s) on driving missing from the Airtable. Please consult the log and fix this problem before continuing.' % missing_from_airtable_count)
        logging.error('This script identified %i record(s) missing from Airtable. Please fix this before continuing.' % missing_from_airtable_count)
    if in_airtable_not_in_library > 0:
        print('ERROR: This script has found %i record(s) on the drive marked as "Deaccessioned Record" in Airtable. Please consult the log and fix this problem before continuing.' % in_airtable_not_in_library)
        logging.error('This script identified %i record(s) on the drive marked as "Deaccessioned Record" in Airtable. Please fix this before continuing.' % in_airtable_not_in_library)
    if missing_from_airtable_count == 0 and in_airtable_not_in_library == 0:
        print('Record level Airtable audit completed succesfully, no errors found. %i record(s) were succesfully located.' % in_airtable_and_in_library)
        logging.info('Record level Airtable audit completed succesfully, no errors found. %i record(s) were succesfully located.' % in_airtable_and_in_library)
        return True
    else:
        logging.info('Record level Airtable audit complete with errors, %i record(s) were succesfully located' % in_airtable_and_in_library)
        return False



def downloadVimeo(airtable, drive_name):
    print('Performing the Download Vimeo subprocess')
    logging.info('Performing the Download Vimeo subprocess')
    success_counter = 0
    warning_counter = 0
    error_counter = 0
    pages = airtable.get_iter()
    for page in pages:
        for record in page:
            UID = record['fields']['Unique ID']
            try:
                in_library = record['fields']['In Library']
            except Exception as e:
                in_library = "Not Found"
            if in_library == "Yes":     #only process records that are in the library
                try:
                    on_drive = record['fields']['On Drive']
                except Exception as e:
                    on_drive = "Not Found"
                if on_drive == "No" or on_drive == "Not Found":     #only process records that are not On Drive
                    try:
                        vimeoLink = record['fields']['Vimeo Link']     #check to see if vimeo link exists
                    except Exception as e:
                        vimeoLink = "No Link"
                        logging.warning('Record ' + UID + ' Marked as In Library and Not On Drive, but no Vimeo Link found. Skipping')
                        warning_counter += 1
                        continue
                    try:
                        vimeoPassword = record['fields']['Vimeo Password']     #check to see if vimeo password exists
                    except Exception as e:
                        vimeoPassword = "No Password"
                    record_id = record['id']
                    try:                                        #checks to see if record has an entry in the File Name field. This will only process empty file names, so as not to overwrite
                        airtable_filename = record['fields']['File Name']
                    except Exception as e:
                        logging.info('Downloading file from Vimeo: %s' % UID)
                    try:                                        #Need to have an try/except here because airtable errors if the field is empty. This is in case there is no Group
                        group = record['fields']['Group']
                    except Exception as e:
                        group = ""
                    if group == "":                             #In case there is no Group, we don't want an extra slash
                        path = os.path.join('/Volumes', drive_name, UID)    #will need to fix this to make it cross platform eventually
                    else:
                        path = os.path.join('/Volumes', drive_name, group, UID)    #will need to fix this to make it cross platform eventually
                    if not os.path.isdir(path):     #see if record path exists, if not make it
                        os.makedirs(path, exist_ok=False)
                        logging.info('Folder for %s created', UID)
                    ydl_command = "youtube-dl -f best -o '" + path + "/%(title)s.%(ext)s' --video-password '" + vimeoPassword + "' " + vimeoLink
                    return_code = subprocess.call(ydl_command, shell=True)
                    if return_code == 0: #success
                        logging.info('Succesfully downloaded file from Vimeo: %s' % UID)
                        update_dict = {'On Drive': "Yes"}
                        try:
                            airtable.update(record_id, update_dict)
                            logging.info('Succesfully updated On Drive to Yes for record %s ' % UID)
                            success_counter += 1
                        except Exception as e:
                            logging.warning('Could not update On Drive field for record %s. Please do this manually!' % UID)
                            warning_counter += 1
                    elif return_code == 1: #fail
                        logging.info('Failed to download file from Vimeo: %s' % UID)
                        error_counter += 1
                    else:                   #idk if this is possible, but putting it in here anyway just in case
                        logging.warning('Something strange happened when trying to download the file from Vimeo: %s' % UID)
                        warning_counter += 1
                    #print(ydl_command) #GOTTA TEST THIS
                else:   #ignore if record is already  "On Drive"
                    continue
            else:   #ignore if record is not "In Library"
                continue

    logging.info('Vimeo download complete, %i files downloaded, %i warnings encountered, %i errors found.' % (success_counter, warning_counter, error_counter))
    return

def fileAudit():
    drive_name = config.DRIVE_NAME
    print('Performing a file-level audit')
    logging.info('Performing a file-level audit')
    missing_file_counter = 0
    file_found_counter = 0
    error_count = 0
    pages = getAirtablePages("Files")

    for page in pages:
        for file in page:
            try:
                record_status = file['fields'][config.RECORD_STATUS_LOOKUP][0]
            except Exception as e:
                record_status = "none"
            if record_status != config.RECORD_DEACCESS_FLAG:     #only process records that are in the library
                RID = file['fields'][config.RECORD_NUMBER_LOOKUP][0]
                try:
                    file_format = file['fields'][config.FILE_FORMAT]
                except Exception as e:
                    file_format = "none"
                if file_format == "Album":
                    try:
                        album_file_count = int(file['fields'][config.FILE_COUNT])
                    except Exception as e:
                        album_file_count = 0
                        logging.warning('Error retreiving file count for album %s from airtable. Please fix this record and continue' % RID)
                file_record_id = file['id']
                try:                                        #checks to see if record has an entry in the File Name field. This will only process empty file names, so as not to overwrite
                    airtable_filename = file['fields'][config.FULL_FILE_NAME]
                except Exception as e:
                    logging.error('Error retreiving file name for record %s. Please fix this record and continue' % RID)
                    error_count += 1
                file_path = os.path.join('/Volumes', drive_name, RID, airtable_filename)    #will need to fix this to make it cross platform eventually
                if os.path.isfile(file_path):
                    file_found_counter += 1
                elif os.path.isdir(file_path) and file_format == "Album":
                    temp_count = 0
                    for f in os.listdir(file_path):
                        if not f.startswith('.'):
                            temp_count += 1
                    if album_file_count ==  temp_count:
                        file_found_counter += 1
                    else:
                        logging.warning('The number of files on the drive in the folder named %s does not match Airtable. Please fix this record and continue' % RID)
                else:
                    logging.error('Filename Mismatch for record %s, file %s. Please fix this before continuing' % (RID, airtable_filename))
                    missing_file_counter += 1
                    error_count += 1

                #files_list = []
                #for f in os.listdir(path):
                #    if os.path.isfile(os.path.join(path, f)):
                #        if not f.startswith('.'):     #avoid hidden files
                #            files_list.append(f)
                #files_list.sort()                      #sort the list so it'll always pick the first file. I think we can get rid of this
                #if len(files_list) > 1 and len(airtable_access_filename) == 0:
                #    logging.warning('Multiple files found in ' + UID + ' but no access copy listed in Airtable, using ' + files_list[0])
                #    if airtable_filename != files_list[0]:
                #        missing_file_counter += 1
                #        logging.error('Filename Mismatch for record %s. Please fix this before continuing' % UID)
                #if len(files_list) == 0:
                #    logging.error('No files found in %s' % RID)
                #    missing_file_counter += 1
                #else:
                #    if airtable_filename != files_list[0]:
                #        missing_file_counter += 1
                #        logging.error('Filename Mismatch for record %s. Please fix this before continuing' % RID)

    if error_count > 0:
        logging.error('File-level audit complete, %i errors found.' % error_count)
        return False
    else:
        logging.info('File-level audit complete, 0 errors found.')
        return True

def validateChecksums():
    #this has been succesfull updated
    #This section validates file checksums and updates the "last validated date" field
    #For now it will only get the first filename, and warns if there is more than one file in the folder
    drive_name = config.DRIVE_NAME
    airtable = Airtable(config.BASE_ID, "Files", config.API_KEY)
    print('Validating Checksums and updating airtable')
    logging.info('Validating Checksums and updating airtable')
    update_counter = 0
    checksum_error_counter = 0
    checksum_validate_counter = 0
    pages = getAirtablePages("Files")

    file_dict_list = []    #need to put everything in a list of dicts so that airtable doesn't time out
    for page in pages:
        for at_file in page:
            try:
                record_status = at_file['fields'][config.RECORD_STATUS_LOOKUP][0]
            except Exception as e:
                record_status = "none"
            try:
                file_format = at_file['fields'][config.FILE_FORMAT]
            except Exception as e:
                file_format = "none"
            if file_format == "Album":    #we can skip this whole process for Albums, they don't have checksums
                continue
            if record_status != config.RECORD_DEACCESS_FLAG:     #only process records that are in the library and aren't albums
                file_record_id = at_file['id']
                RID = at_file['fields'][config.RECORD_NUMBER_LOOKUP][0]
                try:                                        #checks to see if record has an entry in the File Name field. This will only process empty file names, so as not to overwrite
                    airtable_filename = at_file['fields'][config.FULL_FILE_NAME]
                except Exception as e:
                    logging.error('Error retreiving file name for record %s. Please fix this record and continue' % RID)
                    error_count += 1
                try:                                        #checks to see if record has an entry in the checksum field. This will only process records with existing checksums
                    airtable_checksum = at_file['fields'][config.CHECKSUM]
                except Exception as e:
                    logging.warning('No Checksum found for record %s. Skipping validation. Please run checksum creation subprocess to ensure records are up to date.' % (RID))
                    continue
                file_path = os.path.join('/Volumes', drive_name, RID, airtable_filename)    #will need to fix this to make it cross platform eventually
                file_dict = {"RID": RID, "file_record_id": file_record_id, "airtable_checksum": airtable_checksum, "file_path": file_path}
                file_dict_list.append(file_dict)

    file_dict_list_sorted = sorted(file_dict_list, key=lambda d: d['RID'])     #sorts the list so the user can see the big numbers go up!
    for file_dict_entry in file_dict_list_sorted:
        #these next four lines are just here to show how to access dictionary entries for file info from airtable
        #print("RID: " + file_dict_entry["RID"])
        #print("file_record_id: " + file_dict_entry["file_record_id"])
        #print("airtable_checksum: " + file_dict_entry["airtable_checksum"])
        #print("file_path: " + file_dict_entry["file_path"])

        file_checksum = generateHash(file_dict_entry["file_path"]) #this is where we actually get the checksum
        if file_checksum == file_dict_entry["airtable_checksum"]:
            logging.info('Checksum validation succesful for record %s' % file_dict_entry["RID"])
            update_dict = {config.CHECKSUM_VALID: 'Yes', config.CHECKSUM_VALID_DATE: datetime.today().strftime('%Y-%m-%d')}
            checksum_validate_counter += 1
        else:
            logging.error('Checksum validation failed for record %s' % file_dict_entry["RID"])
            update_dict = {config.CHECKSUM_VALID: 'No', config.CHECKSUM_VALID_DATE: datetime.today().strftime('%Y-%m-%d')}
            checksum_error_counter += 1

        #THIS IS THE IMPORTANT BIT WHERE WE UPDATE THE TABLE!
        try:
            airtable.update(file_dict_entry["file_record_id"], update_dict)
            logging.info('Succesfully updated checksum validation date for record %s ' % file_dict_entry["RID"])
            update_counter += 1
        except Exception as e:
            print(e)
            logging.error('Could not update checksum validation for record %s' % file_dict_entry["RID"])
            checksum_error_counter += 1

    logging.info('Checksum Validation complete. %i records succesfully validated, %i Airtable records updated, %i errors encountered. ' % (checksum_validate_counter, update_counter, checksum_error_counter))
    return

def deaccession():
    print('Performing deaccession')
    logging.info('Performing deaccession')
    drive_name = config.DRIVE_NAME
    airtable = Airtable(config.BASE_ID, "Records", config.API_KEY)
    airtable_files = Airtable(config.BASE_ID, 'Files', config.API_KEY)
    deaccession_errors = 0
    deaccession_success = 0
    airtable_files_deleted = 0
    airtable_errors = 0
    pages = airtable.get_iter()
    trash_path = os.path.join('/Volumes', drive_name, "_Trash")
    if os.path.isdir(trash_path):
        logging.info('Trash folder already exists')
    else:
        os.makedirs(trash_path, exist_ok=False)
        logging.info('New trash folder created')
    for page in pages:
        for record in page:
            try:
                record_status = record['fields'][config.RECORD_STATUS]
            except Exception as e:
                record_status = "None"
            if record_status == "Deaccessioned Record":     #look for deaccessioned records
                record_id = record['id']
                RID = record['fields'][config.RECORD_NUMBER]
                path = os.path.join('/Volumes', drive_name, RID)    #will need to fix this to make it cross platform eventually
                if os.path.isdir(path):
                    logging.info('Deaccessioning record %s' % RID)
                    try:
                        shutil.move(path,trash_path)
                        deaccession_success += 1
                        logging.info('Succesfully removed record %s from drive: %s' % (RID, config.DRIVE_NAME))
                    except Exception as e:
                        logging.error('Could not remove record %s from drive %s' % (RID, config.DRIVE_NAME))
                        deaccession_errors += 1
                    try:
                        airtable_file_id_list = record['fields'][config.FILES_IN_RECORD]
                        for f_id in airtable_file_id_list:
                            try:
                                airtable.delete(f_id)
                                logging.info('Succesfully removed file records related to %s from Airtable' % RID)
                                airtable_files_deleted += 1
                            except:
                                logging.error('Could not remove file records related to %s from Airtable' % RID)
                                airtable_errors += 1
                    except:
                        logging.warning('No Airtable file records related to %s. This is not necessarily a problem' % RID)
                else:
                    pass        #if the record isn't found on the drive there's no need to deaccession


    logging.info('Auto deaccession complete. %i records succesfully deaccessioned, %i errors encountered. %i Airtable file records deleted, %i Airtable errors encountered' % (deaccession_success, deaccession_errors, airtable_files_deleted, airtable_errors))
    return

def getChecksums():
    #This section harvests file checksums and puts them in Airtable's Checksum field
    #For now it will only get the first filename, and warns if there is more than one file in the folder
    drive_name = config.DRIVE_NAME
    airtable = Airtable(config.BASE_ID, "Files", config.API_KEY)
    print('Harvesting Checksums and updating airtable')
    logging.info('Harvesting Checksums and updating airtable')
    update_counter = 0
    checksum_counter = 0
    warning_counter = 0
    error_counter = 0
    pages = getAirtablePages("Files")

    file_dict_list = []
    for page in pages:
        for at_file in page:
            try:
                record_status = at_file['fields'][config.RECORD_STATUS_LOOKUP][0]
            except Exception as e:
                record_status = "none"
            try:
                file_format = at_file['fields'][config.FILE_FORMAT]
            except Exception as e:
                file_format = "none"
            if file_format == "Album":    #we can skip this whole process for Albums, they don't have checksums
                continue
            if record_status != config.RECORD_DEACCESS_FLAG:     #only process records that are in the library
                file_record_id = at_file['id']
                RID = at_file['fields'][config.RECORD_NUMBER_LOOKUP][0]
                try:                                        #checks to see if record has an entry in the File Name field. This will only process empty file names, so as not to overwrite
                    airtable_filename = at_file['fields'][config.FULL_FILE_NAME]
                except Exception as e:
                    logging.error('Error retreiving file name for record %s. Please fix this record and continue' % RID)
                    error_count += 1
                try:                                        #checks to see if record has an entry in the checksum field. This will only process records with existing checksums
                    airtable_checksum = at_file['fields'][config.CHECKSUM]
                    continue
                except Exception as e:
                    logging.info('No Checksum found for record %s . Checksum will be harvested.' % (RID))
                file_path = os.path.join('/Volumes', drive_name, RID, airtable_filename)    #will need to fix this to make it cross platform eventually
                file_dict = {"RID": RID, "file_record_id": file_record_id, "file_path": file_path}
                file_dict_list.append(file_dict)

    if len(file_dict_list) == 0:
        logging.info('All files in Airtable have checksums. No checksums will be updated. If you would like to regenerate checksums please remove the data in the "%s" field in Airtable and run this subprocess again.' % config.CHECKSUM)
    else:
        file_dict_list_sorted = sorted(file_dict_list, key=lambda d: d['RID'])     #sorts the list so the user can see the big numbers go up!
        for file_dict_entry in file_dict_list_sorted:
            #these next four lines are just here to show how to access dictionary entries for file info from airtable
            #print("RID: " + file_dict_entry["RID"])
            #print("file_record_id: " + file_dict_entry["file_record_id"])
            #print("airtable_checksum: " + file_dict_entry["airtable_checksum"])
            #print("file_path: " + file_dict_entry["file_path"])

            try:
                checksum = generateHash(file_dict_entry["file_path"])
                update_dict = {config.CHECKSUM: checksum}
                checksum_counter += 1
            except Exception as e:
                logging.error('Could not gather checksums for record %s, filename %s. Check that filename is correct' % (file_dict_entry["RID"], file_dict_entry["file_path"]))
                error_counter += 1
                continue

            #THIS IS THE IMPORTANT BIT WHERE WE UPDATE THE TABLE!
            try:
                airtable.update(file_dict_entry["file_record_id"], update_dict)
                logging.info('Succesfully updated checksum for record %s ' % file_dict_entry["RID"])
                update_counter += 1
            except Exception as e:
                logging.error('Could not update checksums for record %s' % file_dict_entry["RID"])
        logging.info('Checksum harvest complete. %i checksums generated, %i Airtable records updated, %i warnings encountered, %i errors encountered.' % (checksum_counter, update_counter, warning_counter, error_counter))
    return

#This is not really necessary anymore because all record folders are at the root level
#def findRecord(UID, drive_name):
    # Performs the find subprocess. Returns the full path of the record folder.
    # It will first look for the file in a group, if it can't find it in a group it looks as the root level
    # If it can't find it anywhere it throws an error

#    p = pathlib.Path('/Volumes/' + drive_name).glob('**/' + UID)
#    files = [x for x in p if x.is_dir()]
#    nontrash_Records = []   #making a list of records not in the trash can
#    for file in files:
#        if '_Trash' not in str(file):
#            nontrash_Records.append(file)
#    if len(nontrash_Records) == 1:
#        #print(str(files[0]))                                            #commented out standard output
#        logging.info('Record %s found at: %s' % (UID, str(nontrash_Records[0])))
#    elif len(nontrash_Records) == 0:
#        #print('ERROR: Record %s not found' % (UID))                     #commented out standard output
#        logging.error('Record %s not found' % (UID))
#    elif len(nontrash_Records) > 1:
        #print('ERROR: Multiple versions of record %s found at the following locations:' % (UID))    #commented out standard output
#        logging.error('Multiple versions of %s found at the following locations:' % (UID))
#        for file in nontrash_Records:
            #print('%s' % (str(file)))                                   #commented out standard output
#            logging.error('%s' % (str(file)))

def uploadVimeo(airtable, v, drive_name, quantity):
    # Uploads videos from airtable records to vimeo
    # Uses the description, title, location, and dancers to fill out the vimeo details
    # You cannot choose a file to upload, the script will simply start uploading them in order as it finds records with "Yes" as Uplaod to Vimeo but not Vimeo Link
    # The script will automatically run on 5 files and then quit, but you can define how many files you want it to run on
    print('Uploading files to Vimeo')
    logging.info('Uploading files to Vimeo')
    update_counter = 0
    upload_counter = 0
    warning_counter = 0
    error_counter = 0
    pages = airtable. get_iter()
    for page in pages:
        for record in page:
            if upload_counter == quantity:
                break
            try:
                in_library = record['fields']['In Library']
            except Exception as e:
                in_library = "Not Found"
            if in_library == "Yes":     #only process records that are in the library
                record_id = record['id']
                UID = record['fields']['Unique ID']
                try:                                        #checks to see if record has an entry in the Checksum field. This will only process files with no checksum already, so as not to overwrite
                    airtable_vimeo_link = record['fields']['Vimeo Link']
                    continue
                except Exception as e:
                    logging.info('Uploading file to Vimeo for record %s' % UID)
                try:            #first, see if an access copy filename exists. If it does we're gonna use this instead.
                    airtable_filename = record['fields']['Access Copy File Name']
                    logging.info('Found an access copy filename for %s. The access copy will be uploaded to vimeo instead of the main file.' % UID)
                except Exception as e:
                    try:        #if no access copy filename then move ahead with the main file
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

                # This section harvests info from airtable to populate the vimeo record
                try:
                    airtable_vimeo_access = record['fields']['Vimeo Accessiblity']
                except:
                    airtable_vimeo_access = "Private"
                try:
                    airtable_title = record['fields']['Title']
                except:
                    airtable_title = ""
                try:
                    airtable_description = record['fields']['Description']
                except:
                    airtable_description = ""
                try:
                    airtable_vimeo_password = record['fields']['Vimeo Password']
                except:
                    if airtable_vimeo_access == "Private":
                        airtable_vimeo_password = "Charya#1dance"
                    else:
                        airtable_vimeo_password = ""
                try:
                    airtable_date = record['fields']['Date']
                except:
                    airtable_date = ""

                if airtable_description == "" and airtable_date == "":
                    full_description = config.VIMEO_DEFAULT_DESCRIPTION
                elif airtable_description == "":
                    full_description = "Date Created: " + airtable_date + "\n\n" + config.VIMEO_DEFAULT_DESCRIPTION
                elif airtable_date == "":
                    full_description = airtable_description + "\n\n" + config.VIMEO_DEFAULT_DESCRIPTION
                else:
                    full_description = airtable_description + "\n\nDate Created: " + airtable_date + "\n\n" + config.VIMEO_DEFAULT_DESCRIPTION
                # THIS IS WHERE WE'LL UPLOAD THE FILE TO VIMEO
                try:
                    if airtable_vimeo_access == "Public":
                        vimeoDict = {'name': airtable_title, 'description': full_description, 'privacy':{'view' : 'anybody'}}
                    elif airtable_vimeo_access == "Only Me":
                        vimeoDict = {'name': airtable_title, 'description': full_description, 'privacy':{'view' : 'nobody'}}
                    elif airtable_vimeo_access == "Private":
                        vimeoDict = {'name': airtable_title, 'description': full_description, 'privacy':{'view' : 'password'}, 'password': airtable_vimeo_password}
                    else:
                        vimeoDict = {'name': airtable_title, 'description': full_description, 'privacy':{'view' : 'nobody'}}
                    #logging.info('Uploading file: %s' % file_path)
                    video_uri = v.upload(file_path,data=vimeoDict)
                    vimeo_link = 'https://vimeo.com/' + video_uri.split('/')[-1]
                    update_dict = {'Vimeo Link': vimeo_link}
                    upload_counter += 1
                except Exception as e:
                    logging.error('Could not upload file to Vimeo for record %s.' % UID)
                    logging.error(e)
                    #logging.error(vimeoDict)
                    error_counter += 1
                    continue

                #THIS IS THE IMPORTANT BIT WHERE WE UPDATE THE TABLE!

                try:
                    airtable.update(record_id, update_dict)
                    logging.info('Succesfully added Vimeo link for record %s ' % UID)
                    update_counter += 1
                    pages = airtable.get_iter() # Need to do this in order to refresh the token, which breaks after a certain period of time
                except Exception as e:
                    logging.error('Could not added Vimeo link for record %s' % UID)
                    logging.error('%s' % e)
    logging.info('Vimeo Upload. %i files uploaded, %i Airtable records updated, %i warnings encountered, %i errors encountered.' % (upload_counter, update_counter, warning_counter, error_counter))
    return


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
