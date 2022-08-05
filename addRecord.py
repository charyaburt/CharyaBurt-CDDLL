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
    parser.add_argument('-b', '--Batch',dest='b',action='store_true',default=False,help="turns on Batch mode, which runs the script in a loop until all new records have been added")
    #parser.add_argument('-r', '--Record',dest='r',action='store',default=None,help="Set the record ID you want to add to the archive")
    #parser.add_argument('-f', '--File',dest='f',action='store',default=None,help="Sets the filepath of the file you want to add to the archive")
    args = parser.parse_args()

    if args.d:
        log_level=logging.DEBUG
    else:
        log_level=logging.INFO

    levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]     #The default verbosity level for stdout is CRITICAL
    verbose_level = levels[min(len(levels)-1,args.verbose)]

    logDir = os.getcwd()               # The log will be created at the working directory
    logName = 'addRecord_' + datetime.today().strftime('%Y-%m-%d')  # The script will be named log.log
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

    #Perform a record-level audit of the drive. Quit upon failure
    #if not driveAudit():
    #    quit()

    #Performs a record-level audit of the airtable. Quit upon failure
    #if not airtableAudit():
    #    quit()

    #Creates list of records to be processed
    record_dict_list = findRecordToAdd()

    if not record_dict_list:    #if list is empty
        logging.info("No records are labeled as ready to update in Airtable (Intaking Local Data File). Please make sure to follow the proper workflow for adding a record to Airtable and try again")
        quit()

    post_process_list = []

    if args.b == True:
        logging.info("Running in batch mode!")
    for record_dict in record_dict_list:
        if not createRecordFolder(record_dict['RID']):  #quit upon error
            quit()
        pres_file_path = verifyUserAddedFile(record_dict)    #this portion verifies that file is correct and returns the filepath
        if not pres_file_path:
            logging.error("There was an error retreiving the file path for the file in folder %s. Please try again" % record_dict_list[0]['RID'])
            quit()
        else:
            file_id = processRecord(pres_file_path, record_dict)
            post_process_list.append({"file_id": file_id, "post_file_path": pres_file_path, "post_RID": record_dict['RID']})
        if args.b == False:
            break

    logging.info("Processing checksums, this may take a while, check back in a few minutes")
    for post_process_dict in post_process_list:
        file_checksum = generateHash(post_process_dict["post_file_path"])
        updateAirtableField(post_process_dict["file_id"], {config.CHECKSUM: file_checksum}, post_process_dict["post_RID"], "Files")

    logging.critical('========Script Complete========')

## End of main function

def processRecord(pres_file_path, record_dict_entry):
    #returns the record id, which we need later for updating the checksum
    pres_mediainfo_text = getMediaInfo(pres_file_path)
    pres_airtable_create_dict = parseMediaInfo(pres_file_path, pres_mediainfo_text, record_dict_entry['RID'], record_dict_entry['record_id'])
    #reason_list = []       #list of reasons to create access files. is empty if no need for access file
    #reason_list = checkForAccessFile(pres_airtable_create_dict)
    #if not reason_list:
    #    logging.info("No access copy needed. Creating airtable entry for file information")
    pres_airtable_create_dict[config.COPY_VERSION] = "Master Copy"
    #pres_airtable_create_dict[config.USE_FOR_ACCESS] = "Yes"
    file_record = createAirtableFileRecord(pres_airtable_create_dict)
    if file_record != False:
        logging.info("Finished creating airtable file entries for %s." % record_dict_entry['RID'])
        print("Finished creating airtable file entries for %s." % record_dict_entry['RID'])
        updateAirtableField(record_dict_entry['record_id'],{config.FILE_PROCESS_STATUS: None},record_dict_entry['RID'], "Records")   #sets FILE_PROCESS_STATUS to blank because we're done!
    else:
        logging.error("Error creating airtable file entries for %s." % record_dict_entry['RID'])
        print("Error creating airtable file entries for %s. See log for details" % record_dict_entry['RID'])
    #else:   #if we need to create an access file, we do the following
    #    pres_airtable_create_dict[config.COPY_VERSION] = "Master Copy"
    #    pres_airtable_create_dict[config.USE_FOR_ACCESS] = "No"
    #    access_file_path = createAccessFile(pres_file_path, pres_airtable_create_dict, reason_list)
    #    access_mediainfo_text = getMediaInfo(access_file_path)
    #    access_airtable_create_dict = parseMediaInfo(access_file_path, access_mediainfo_text, record_dict_entry['RID'], record_dict_entry['record_id'])
    #    access_airtable_create_dict[config.COPY_VERSION] = "Access Copy"
    #    access_airtable_create_dict[config.USE_FOR_ACCESS] = "Yes"
    #    if createAirtableFileRecord(pres_airtable_create_dict) and createAirtableFileRecord(access_airtable_create_dict):
    #        logging.info("Finished creating airtable file entries for %s." % record_dict_entry['RID'])
    #        print("Finished creating airtable file entries for %s." % record_dict_entry['RID'])
    #        updateAirtableField(record_dict_entry['record_id'],{config.FILE_PROCESS_STATUS: None},record_dict_entry['RID'], "Records")   #sets FILE_PROCESS_STATUS to blank because we're done!
    #    else:
    #        logging.error("Error creating airtable file entries for %s." % record_dict_entry['RID'])
    #        print("Error creating airtable file entries for %s. See log for details" % record_dict_entry['RID'])
    return file_record["id"]

def checkForAccessFile(airtable_create_dict):
    # NOT USING THIS ANYMORE IN THIS SCRIPT. MOVING TO UPLOAD SCRIPT
    reason_list = []
    if "Interlaced" in airtable_create_dict[config.VIDEO_SCAN_TYPE]: #needs access file if it's interlaced
        reason_list.append("Interlaced")
    if int(airtable_create_dict[config.FILE_SIZE]) > config.MAX_SIZE: #needs access file if it's too big
        reason_list.append("Large")
    if airtable_create_dict[config.VIDEO_CODEC] == "None": #needs access file if it's too big
        reason_list.append("No Video")
    return reason_list

def createAccessFile(filePath, airtable_create_dict, reason_list):
    #creates access file. returns access file path
    fileNameExtension = filePath.split(".")[-1]
    accessFilePath = filePath.split("." + fileNameExtension)[0] + "_access.mp4"
    ffmpeg_base = config.FFMPEG_PATH + " -hide_banner -loglevel panic -i "
    ffmpeg_middle = ""
    if "No Video" in reason_list:
        logging.info('File %s has no video, creating a video version for access file.' % airtable_create_dict[config.FILENAME])
        ffmpeg_middle = "-filter_complex '[0:a]showwaves=s=640x480,format=yuv420p[vid]' -map '[vid]' -map 0:a -codec:v libx264 -crf 25 -preset fast -codec:a aac -strict -2 -b:a 192k -y"
    elif "Interlaced" in reason_list and "Large" in reason_list:
        logging.info('File named %s is Interlaced and over 5GB. Making a smaller Progressive access file' % airtable_create_dict[config.FILENAME])
        ffmpeg_middle = "-c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -vf yadif -s 640x480 -aspect %s -y" % airtable_create_dict[config.VIDEO_ASPECT_RATIO]
    elif "Interlaced" in reason_list:
        logging.info('File named %s is Interlaced. Making a Progressive access file' % airtable_create_dict[config.FILENAME])
        ffmpeg_middle = "-c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -vf yadif -y"
    elif "Large" in reason_list:
        logging.info('File named %s is larger than max limit (%i Bytes). Making a smaller access file' % ((airtable_create_dict[config.FILENAME]), config.MAX_SIZE))
        ffmpeg_middle = "-c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -s 640x480 -aspect %s -y" % airtable_create_dict[config.VIDEO_ASPECT_RATIO]


    ffmpeg_string = "%s '%s' %s '%s'" %(ffmpeg_base, filePath, ffmpeg_middle, accessFilePath)
    logging.info("Running FFmpeg command: %s" % ffmpeg_string)
    cmd = [ffmpeg_string]
    ffmpeg_out = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
    logging.info("Finished Running FFmpeg command")
    return accessFilePath
    #ffmpeg -i input.mp4 -filter_complex "[0:a]showwaves=s=1280x720,format=yuv420p[vid]" -map "[vid]" -map 0:a -codec:v libx264 -crf 18 -preset fast -codec:a aac -strict -2 -b:a 192k output.mp4

def getMediaInfo(filePath):
    cmd = [ config.MEDIAINFO_PATH, '-f', '--Output=XML', filePath ]
    media_info = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
    return media_info

def verifyUserAddedFile(record_dict):
    #Verifies that the file added by the user conforms to proper specifications
    #returns the path to the file if all is good, returns None otherwise
    drive_name = config.DRIVE_NAME
    record_path = os.path.join('/Volumes', drive_name, record_dict['RID'])
    logging.info('Please add in the file you would like processing into the folder named %s. Once you have done so you may press enter to continue. You can also type "skip" to cancel.' % record_dict['RID'])
    userInput = input('Please add in the file you would like processing into the folder named %s. Once you have done so you may press enter to continue. You can also type "skip" to cancel. \n' % record_dict['RID'])
    if userInput == "skip":
        return None

    #This first section makes sure that only one file is in the folder

    file_list = []
    for f in os.listdir(record_path):
        if not f.startswith('.'):
            file_list.append(f)
    while len(file_list) == 0:
        logging.error('No file found in folder named %s. Please add a file to the folder and press any key to continue. You can also type "skip" to cancel.' % record_dict['RID'])
        userInput = input('ERROR: No file found in folder named %s. Please add a file to the folder and press any key to continue. You can also type "skip" to cancel. \n' % record_dict['RID'])
        if userInput == "skip":
            return None
        file_list = []
        for f in os.listdir(record_path):
            if not f.startswith('.'):
                file_list.append(f)
    while len(file_list) > 1:
        logging.error('%i files found in folder named %s. Make sure only one file is in the folder and press any key to continue. You can also type "skip" to cancel.' % (len(file_list), record_dict['RID']))
        userInput = input('ERROR: %i files found in folder named %s. Make sure only one file is in the folder and press any key to continue. You can also type "skip" to cancel. \n' % (len(file_list), record_dict['RID']))
        if userInput == "skip":
            return None
        file_list = []
        for f in os.listdir(record_path):
            if not f.startswith('.'):
                file_list.append(f)

    #This sections makes sure that there are no single or double quotes in the file name

    while "\'" in file_list[0] or "\"" in file_list[0] or "`" in file_list[0]:
        logging.error('The selected file has double quotes, single quotes, apostrophes, or ticks. Please remove these llegalar characters befor continuing. You can also type "skip" to cancel.')
        userInput = input('ERROR: The selected file has double quotes, single quotes, apostrophes, or ticks. Please remove these llegalar characters befor continuing. You can also type "skip" to cancel. \n')
        if userInput == "skip":
            return None
        file_list = []
        for f in os.listdir(record_path):
            if not f.startswith('.'):
                file_list.append(f)

    return os.path.join('/Volumes', drive_name, record_dict['RID'], file_list[0])

def updateAirtableField(record_id, update_dict, RID, Table):
    airtable = Airtable(config.BASE_ID, Table, config.API_KEY)
    try:
        airtable.update(record_id, update_dict)
        logging.info('Succesfully updated field in table %s \'%s\' for record %s ' % (Table, str(list(update_dict.keys())[0]), RID))
    except Exception as e:
        logging.error('Could not updated field in table %s \'%s\' for record %s ' % (Table, str(list(update_dict.keys())[0]), RID))
        logging.error('%s' % e)

def createRecordFolder(record_number):
    #Creates a folder on the drive for the record being processed
    logging.info('Creating folder for record: %s.' % record_number)
    drive_name = config.DRIVE_NAME
    newpath = os.path.join('/Volumes', drive_name, record_number)
    drivepath = os.path.join('/Volumes', drive_name)
    if not os.path.exists(drivepath):
        logging.error('Drive not found. Check that drive is mounted and make sure drive name is correct in config.py')
        return False
    if not os.path.exists(newpath):
        try:
            os.makedirs(newpath)
            return True
        except:
            logging.error('Error creating folder')
            return False
    else:
        logging.error('Folder Already Exists. Exiting Script')
        print("Script exited because of an error. See log for details")
        return False


def findRecordToAdd():
    #This performs a quick drive audit, checking to see if drive contains every reord labeled as "in library" in airtableAudit
    drive_name = config.DRIVE_NAME
    logging.info('Looking for new records to add to drive named: %s.' % drive_name)
    record_dict_list = []
    pages = getAirtablePages("Records")
    for page in pages:
        for record in page:
            RID = record['fields'][config.RECORD_NUMBER]
            try:
                file_process_status = record['fields'][config.FILE_PROCESS_STATUS]
                if file_process_status == 'Intaking Local Data File':
                    record_id = record['id']
                    record_dict = {"RID": RID, "record_id": record_id}
                    record_dict_list.append(record_dict)
            except Exception as e:
                file_process_status = False

    record_dict_list_sorted = sorted(record_dict_list, key=lambda d: d['RID'])
    return record_dict_list_sorted


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
    for page in pages:
        for record in page:
            try:
                in_library = record['fields'][config.IN_LIBRARY]
            except Exception as e:
                in_library = "Not Found"
            if in_library == "Yes":     #only process records that are in the library
                RID = record['fields'][config.RECORD_NUMBER]
                path = os.path.join('/Volumes', drive_name, RID)    #will need to fix this to make it cross platform eventually
                if not os.path.isdir(path):
                    logging.error('Could not find record %s' % RID)
                    missing_from_drive_count += 1
                else:
                    correct_on_drive_count += 1
    if missing_from_drive_count > 0:
        print('ERROR: Record level drive audit has found %i missing record(s). Please consult the log and fix this problem before continuing. %i record(s) were succesfully located' % (missing_from_drive_count, correct_on_drive_count))
        logging.error('Record level drive audit has identified %i missing record(s). Please fix this before attempting to add any records.' % missing_from_drive_count)
        logging.info('%i record(s) were succesfully located' % correct_on_drive_count)
        logging.critical('========Script Complete========')
        return False
    else:
        print('Record level drive audit completed. %i record(s) were succesfully located' % correct_on_drive_count)
        logging.info('Record level drive audit completed succesfully. %i record(s) were succesfully located' % correct_on_drive_count)
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
                in_library = record['fields'][config.IN_LIBRARY]
            except Exception as e:
                in_library = "No"
            record_dict.update({RID: in_library})

    drive_path = os.path.join('/Volumes', drive_name)
    for item in os.listdir(drive_path):
        if os.path.isdir(os.path.join(drive_path, item)):
            if item.startswith("CB"):
                found_in_airtable = False       # initiate found boolean as false
                if item in record_dict:
                    if record_dict.get(item) == "Yes":
                        in_airtable_and_in_library += 1
                        #logging.debug('Record %s was found in Airtable' % item)
                    else:
                        in_airtable_not_in_library += 1
                        logging.error('Record %s was found in Airtable but was labeled "Not In Library" despite being on the drive' % item)
                else:
                    logging.error('Could not find record %s on the Airtable' % item)
                    missing_from_airtable_count += 1
    if missing_from_airtable_count > 0:
        print('ERROR: This script has found %i record(s) on driving missing from the Airtable. Please consult the log and fix this problem before continuing.' % missing_from_airtable_count)
        logging.error('This script identified %i record(s) missing from Airtable. Please fix this before continuing.' % missing_from_airtable_count)
    if in_airtable_not_in_library > 0:
        print('ERROR: This script has found %i record(s) on the drive marked as "Not In Library" in Airtable. Please consult the log and fix this problem before continuing.' % in_airtable_not_in_library)
        logging.error('This script identified %i record(s) on the drive marked as "Not In Library" in Airtable. Please fix this before continuing.' % in_airtable_not_in_library)
    if missing_from_airtable_count == 0 and in_airtable_not_in_library == 0:
        print('Record level Airtable audit completed succesfully, no errors found. %i record(s) were succesfully located.' % in_airtable_and_in_library)
        logging.info('Record level Airtable audit completed succesfully, no errors found. %i record(s) were succesfully located.' % in_airtable_and_in_library)
        return True
    else:
        logging.info('Record level Airtable audit complete with errors, %i record(s) were succesfully located' % in_airtable_and_in_library)
        logging.info('Please fix these errors before continuing')
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

def getAirtablePages(table_name):
    #takes table name, returns pages.
    #BASE_ID and API_KEY come from config.py file.
    airtable = Airtable(config.BASE_ID, table_name, config.API_KEY)
    pages = airtable.get_iter()
    return pages

def parseMediaInfo(filePath, media_info_text, RID, parent_id):
    # The following line initializes the dict.
    parent_id_array = [parent_id]   #for some reason airatble needs this as an array.
    airtable_create_dict = {config.PARENT_ID : parent_id_array, config.FULL_FILE_NAME : "", config.FILENAME : "", config.DURATION : "", config.FILE_SIZE_STRING : "", config.FILE_SIZE : "", config.FILE_FORMAT : "", config.VIDEO_CODEC : "", config.VIDEO_BIT_DEPTH : "", config.VIDEO_SCAN_TYPE : "", config.VIDEO_FRAME_RATE : "", config.VIDEO_FRAME_SIZE : "", config.VIDEO_ASPECT_RATIO : "",  config.AUDIO_SAMPLING_RATE : "", config.AUDIO_CODEC : "", config.COPY_VERSION : ""}
    fileNameTemp = os.path.basename(filePath)
    airtable_create_dict[config.FULL_FILE_NAME] = fileNameTemp
    fileNameExtension = fileNameTemp.split(".")[-1]
    airtable_create_dict[config.FILENAME] = fileNameTemp.split("." + fileNameExtension)[0]
    media_info_text = media_info_text.decode()
    logging.info("Parsing mediainfo for file: %s" % airtable_create_dict[config.FILENAME])

    try:
        mi_General_Text = (media_info_text.split("<track type=\"General\">"))[1].split("</track>")[0]

        try:
            mi_Video_Text = (media_info_text.split("<track type=\"Video\">"))[1].split("</track>")[0]
        except:
            logging.warning('Could not parse video track for file %s. If this file is supposed to have video it may be corrupted. The file will be processed as an audio only file' %  airtable_create_dict[config.FILENAME])
            airtable_create_dict[config.VIDEO_CODEC] = "None"
            airtable_create_dict[config.VIDEO_BIT_DEPTH] = "None"
            airtable_create_dict[config.VIDEO_SCAN_TYPE] = "None"
            airtable_create_dict[config.VIDEO_FRAME_RATE] = "None"
            airtable_create_dict[config.VIDEO_FRAME_SIZE] = "None"
            airtable_create_dict[config.VIDEO_ASPECT_RATIO] = "None"
        try:
            mi_Audio_Text = (media_info_text.split("<track type=\"Audio\">"))[1].split("</track>")[0]
        except:
            logging.warning('Could not parse audio track for file %s. If this file is supposed to have audio it may be corrupted. This will be processed as a Video Only file' %  airtable_create_dict[config.FILENAME])
            airtable_create_dict[config.AUDIO_CODEC] = "None"
            airtable_create_dict[config.AUDIO_SAMPLING_RATE] = "None"

    except:
        logging.error("MEDIAINFO ERROR: Could not parse tracks for " + airtable_create_dict[config.FILENAME])

    # General Stuff

    try:
        airtable_create_dict[config.DURATION] = (mi_General_Text.split("<Duration_String3>"))[1].split("</Duration_String3>")[0]
    except:
        logging.error("MEDIAINFO ERROR: Could not parse Duration for " + airtable_create_dict[config.FILENAME])
    try:
        airtable_create_dict[config.FILE_FORMAT] = (mi_General_Text.split("<Format_String>"))[1].split("</Format_String>")[0]
    except:
        logging.error("MEDIAINFO ERROR: Could not File Format for " + airtable_create_dict[config.FILENAME])
    try:
        airtable_create_dict[config.FILE_SIZE_STRING] = (mi_General_Text.split("<FileSize_String4>"))[1].split("</FileSize_String4>")[0]
    except:
        logging.error("MEDIAINFO ERROR: Could not parse File Size for " + airtable_create_dict[config.FILENAME])
    try:
        airtable_create_dict[config.FILE_SIZE] = int((mi_General_Text.split("<FileSize>"))[1].split("</FileSize>")[0])
    except:
        logging.error("MEDIAINFO ERROR: Could not parse File Size for " + airtable_create_dict[config.FILENAME])

        # Video Stuff

    if not airtable_create_dict[config.VIDEO_CODEC] == "None":
        try:
            airtable_create_dict[config.VIDEO_CODEC] = (mi_Video_Text.split("<CodecID>"))[1].split("</CodecID>")[0]
        except:
            logging.error("MEDIAINFO ERROR: Could not parse Video Track Encoding for " + airtable_create_dict[config.FILENAME])
        try:
            airtable_create_dict[config.VIDEO_BIT_DEPTH] = (mi_Video_Text.split("<BitDepth>"))[1].split("</BitDepth>")[0]
        except:
            logging.error("MEDIAINFO ERROR: Could not parse Video Bit Depth for " + airtable_create_dict[config.FILENAME])
        try:
            airtable_create_dict[config.VIDEO_SCAN_TYPE] = (mi_Video_Text.split("<ScanType_String>"))[1].split("</ScanType_String>")[0]
        except:
            logging.error("MEDIAINFO ERROR: Could not parse Scan Type for " + airtable_create_dict[config.FILENAME])
        try:
            airtable_create_dict[config.VIDEO_FRAME_RATE] = (mi_Video_Text.split("<FrameRate>"))[1].split("</FrameRate>")[0]
        except:
            logging.error("MEDIAINFO ERROR: Could not parse Frame Rate for " + airtable_create_dict[config.FILENAME])
        try:
            frame_width = (mi_Video_Text.split("<Width>"))[1].split("</Width>")[0]
        except:
            logging.error("MEDIAINFO ERROR: Could not parse Frame Width for " + airtable_create_dict[config.FILENAME])
        try:
            frame_height = (mi_Video_Text.split("<Height>"))[1].split("</Height>")[0]
        except:
            logging.error("MEDIAINFO ERROR: Could not parse Frame Height for " + airtable_create_dict[config.FILENAME])

        airtable_create_dict[config.VIDEO_FRAME_SIZE] = frame_width + "x" + frame_height

        try:
            airtable_create_dict[config.VIDEO_ASPECT_RATIO] = (mi_Video_Text.split("<DisplayAspectRatio_String>"))[1].split("</DisplayAspectRatio_String>")[0]
        except:
            print("MEDIAINFO ERROR: Could not parse Display Aspect Ratio for " + airtable_create_dict[config.FILENAME])

        # Audio Stuff
    if not airtable_create_dict[config.AUDIO_CODEC] == "None":
        try:
            airtable_create_dict[config.AUDIO_SAMPLING_RATE] = (mi_Audio_Text.split("<SamplingRate>"))[1].split("</SamplingRate>")[0]
        except:
            logging.error("MEDIAINFO ERROR: Could not parse Audio Sampling Rate for " + airtable_create_dict[config.FILENAME])
        try:
            airtable_create_dict[config.AUDIO_CODEC] = (mi_Audio_Text.split("<Codec>"))[1].split("</Codec>")[0]
        except:
            try:
                airtable_create_dict[config.AUDIO_CODEC] = (mi_Audio_Text.split("<Format>"))[1].split("</Format>")[0]
            except:
                logging.error("MEDIAINFO ERROR: Could not parse Audio Track Encoding for " + airtable_create_dict[config.FILENAME])

    #No longer harvesting checksum during this process, doing so after the records are updated
    #try:
    #    airtable_create_dict[config.CHECKSUM] = generateHash(filePath)
    #except:
    #    logging.error("MEDIAINFO ERROR: Could not generate checksum for " + airtable_create_dict[config.FILENAME])

    return airtable_create_dict

def createAirtableFileRecord(pres_airtable_create_dict):
    try:
        airtable = Airtable(config.BASE_ID, "Files", config.API_KEY)
        return airtable.insert(pres_airtable_create_dict)
    except Exception as e:
        logging.error("Could not create an airtable file entry for file %s " % (pres_airtable_create_dict[config.FILENAME]))
        print(e)
        return False



# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
