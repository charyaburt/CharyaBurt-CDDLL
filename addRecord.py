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

    #Perform a record-level audit of the drive. Quit upon failure
    #if not driveAudit():
    #    quit()

    #Performs a record-level audit of the airtable. Quit upon failure
    #if not airtableAudit():
    #    quit()

    #file with no audio
    #filePath = '/Volumes/Morgan G-Drive/VideoProjects/OceansOfPhantasy/_GoodSourceMP4s/C64/FloatingBalls.mp4'
    #file with Audio
    filePath = '/Volumes/Morgan G-Drive/VideoProjects/OceansOfPhantasy/Captures/20180930/Gabe04.mov'
    mediainfo_text = getMediaInfo(filePath)
    #print(mediainfo_text)
    airtable_update_dict = parseMediaInfo(filePath, mediainfo_text, "1234")
    print(airtable_update_dict)
    if checkForAccessFile(airtable_update_dict):
        createAccessFile(filePath, airtable_update_dict)

    quit()

    #Creates list of records to be processed
    record_dict_list = findRecordToAdd()

    if args.b == False:         #single file mode
        if not createRecordFolder(record_dict_list[0]['RID']):  #quit upon error
            quit()
        if not verifyUserAddedFile(record_dict_list[0]):        #quit upon error
            updateAirtableField(record_dict_list[0]['record_id'], {config.FILE_PROCESS_STATUS: None}, record_dict_list[0]['RID'])   #this little bit removes the airtable processing status because the user hit "skip". have to pass "None" to airtable to clear multiple choice selection
            quit()
    else:                       #batch mode
        print(record_dict_list)

    #update_dict = {config.FILE_PROCESS_STATUS: ""}

    logging.critical('========Script Complete========')

## End of main function

def checkForAccessFile(airtable_update_dict):
    if "Interlaced" in airtable_update_dict['video scan type']: #needs access file if it's interlaced
        logging.info('File named %s is Interlaced. Making a Progressive access file' % airtable_update_dict['filename'])
        return True
    if int(airtable_update_dict['file size']) > 5000000000: #needs access file if it's too big
        logging.info('File named %s is larger than 5GB. Making a smaller access file' % airtable_update_dict['filename'])
        return True
    else:
        return False

def createAccessFile(filePath, airtable_update_dict):
    fileNameExtension = filePath.split(".")[-1]
    accessFilePath = filePath.split("." + fileNameExtension)[0] + "_access.mp4"
    ffmpeg_string = "/usr/local/bin/ffmpeg -hide_banner -loglevel panic -i '%s' -c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -vf yadif -y '%s'" %(filePath, accessFilePath)
    logging.info("Running FFmpeg command: %s" % ffmpeg_string)
    cmd = [ffmpeg_string]
    ffmpeg_out = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
    logging.info("Finished Running FFmpeg command")

def getMediaInfo(filePath):
    cmd = [ '/usr/local/bin/mediainfo', '-f', '--Output=XML', filePath ]
    media_info = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
    return media_info

def verifyUserAddedFile(record_dict):
    #Verifies that the file added by the user conforms to proper specifications
    drive_name = config.DRIVE_NAME
    record_path = os.path.join('/Volumes', drive_name, record_dict['RID'])
    userInput = input('Please add in the file you would like processing into the folder named %s. Once you have done so you may press any key to continue. You can also type "skip" to cancel. \n\n' % record_dict['RID'])
    if userInput == "skip":
        return False

    #This first section makes sure that only one file is in the folder

    file_list = []
    for f in os.listdir(record_path):
        if not f.startswith('.'):
            file_list.append(f)
    while len(file_list) == 0:
        userInput = input('ERROR: No file found in folder named %s. Please add a file to the folder and press any key to continue. You can also type "skip" to cancel. \n\n' % record_dict['RID'])
        if userInput == "skip":
            return False
        file_list = []
        for f in os.listdir(record_path):
            if not f.startswith('.'):
                file_list.append(f)
    while len(file_list) > 1:
        userInput = input('ERROR: %i files found in folder named %s. Make sure only one file is in the folder and press any key to continue. You can also type "skip" to cancel. \n\n' % (len(file_list), record_dict['RID']))
        if userInput == "skip":
            return False
        file_list = []
        for f in os.listdir(record_path):
            if not f.startswith('.'):
                file_list.append(f)

    #This sections makes sure that there are no single or double quotes in the file name

    while "\'" in file_list[0] or "\"" in file_list[0] or "`" in file_list[0]:
        userInput = input('ERROR: The selected file has double quotes, single quotes, apostrophes, or ticks. Please remove these llegalar characters befor continuing. You can also type "skip" to cancel. \n\n')
        if userInput == "skip":
            return False
        file_list = []
        for f in os.listdir(record_path):
            if not f.startswith('.'):
                file_list.append(f)

    return True

def updateAirtableField(record_id, update_dict, RID):
    airtable = Airtable(config.BASE_ID, "Records", config.API_KEY)
    try:
        airtable.update(record_id, update_dict)
        logging.info('Succesfully updated field \'%s\' for record %s ' % (str(list(update_dict.keys())[0]), RID))
    except Exception as e:
        logging.error('Could not updated field \'%s\' for record %s ' % (str(list(update_dict.keys())[0]), RID))
        logging.error('%s' % e)

def createRecordFolder(record_number):
    #Creates a folder on the drive for the record being processed
    logging.info('Creating folder for record: %s.' % record_number)
    drive_name = config.DRIVE_NAME
    newpath = os.path.join('/Volumes', drive_name, record_number)
    if not os.path.exists(newpath):
        try:
            os.makedirs(newpath)
            return True
        except:
            logging.error('Error creating folder')
            return False
    else:
        logging.error('Folder Already Exists. Exiting Script')
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

def parseMediaInfo(filePath, media_info_text, file_id):
    # The following line initializes the dict.
    airtable_update_dict = {config.FILENAME : "", config.DURATION : "", config.FILE_SIZE_STRING : "", config.FILE_SIZE : "", config.FILE_FORMAT : "", config.VIDEO_CODEC : "", config.VIDEO_BIT_DEPTH : "", config.VIDEO_SCAN_TYPE : "", config.VIDEO_FRAME_RATE : "", config.VIDEO_FRAME_SIZE : "", config.VIDEO_ASPECT_RATIO : "", config.AUDIO_BIT_DEPTH : "", config.AUDIO_SAMPLING_RATE : "", config.AUDIO_CODEC : ""}
    fileNameTemp = os.path.basename(filePath)
    fileNameExtension = fileNameTemp.split(".")[-1]
    airtable_update_dict[config.FILENAME] = fileNameTemp.split("." + fileNameExtension)[0]
    media_info_text = media_info_text.decode()
    logging.info("Parsing mediainfo for file: %s" % airtable_update_dict[config.FILENAME])

    try:
        mi_General_Text = (media_info_text.split("<track type=\"General\">"))[1].split("</track>")[0]

        try:
            mi_Video_Text = (media_info_text.split("<track type=\"Video\">"))[1].split("</track>")[0]
        except:
            logging.warning('Could not parse video track for file %s. If this file is supposed to have video it may be corrupted' %  airtable_update_dict[config.FILENAME])
        try:
            mi_Audio_Text = (media_info_text.split("<track type=\"Audio\">"))[1].split("</track>")[0]
        except:
            logging.warning('Could not parse audio track for file %s. If this file is supposed to have audio it may be corrupted' %  airtable_update_dict[config.FILENAME])

    except:
        logging.error("MEDIAINFO ERROR: Could not parse tracks for " + airtable_update_dict[config.FILENAME])

    # General Stuff

    try:
        airtable_update_dict[config.DURATION] = (mi_General_Text.split("<Duration_String3>"))[1].split("</Duration_String3>")[0]
    except:
        logging.error("MEDIAINFO ERROR: Could not parse Duration for " + airtable_update_dict[config.FILENAME])
    try:
        airtable_update_dict[config.FILE_FORMAT] = (mi_General_Text.split("<Format_String>"))[1].split("</Format_String>")[0]
    except:
        logging.error("MEDIAINFO ERROR: Could not File Format for " + airtable_update_dict[config.FILENAME])
    try:
        airtable_update_dict[config.FILE_SIZE_STRING] = (mi_General_Text.split("<FileSize_String4>"))[1].split("</FileSize_String4>")[0]
    except:
        logging.error("MEDIAINFO ERROR: Could not parse File Size for " + airtable_update_dict[config.FILENAME])
    try:
        airtable_update_dict[config.FILE_SIZE] = (mi_General_Text.split("<FileSize>"))[1].split("</FileSize>")[0]
    except:
        logging.error("MEDIAINFO ERROR: Could not parse File Size for " + airtable_update_dict[config.FILENAME])

        # Video Stuff

    try:
        airtable_update_dict[config.VIDEO_CODEC] = (mi_Video_Text.split("<CodecID>"))[1].split("</CodecID>")[0]
    except:
        logging.error("MEDIAINFO ERROR: Could not parse Video Track Encoding for " + airtable_update_dict[config.FILENAME])
    try:
        airtable_update_dict[config.VIDEO_BIT_DEPTH] = (mi_Video_Text.split("<BitDepth>"))[1].split("</BitDepth>")[0]
    except:
        logging.error("MEDIAINFO ERROR: Could not parse Video Bit Depth for " + airtable_update_dict[config.FILENAME])
    try:
        airtable_update_dict[config.VIDEO_SCAN_TYPE] = (mi_Video_Text.split("<ScanType_String>"))[1].split("</ScanType_String>")[0]
    except:
        logging.error("MEDIAINFO ERROR: Could not parse Scan Type for " + airtable_update_dict[config.FILENAME])
    try:
        airtable_update_dict[config.VIDEO_FRAME_RATE] = (mi_Video_Text.split("<FrameRate>"))[1].split("</FrameRate>")[0]
    except:
        logging.error("MEDIAINFO ERROR: Could not parse Frame Rate for " + airtable_update_dict[config.FILENAME])
    try:
        frame_width = (mi_Video_Text.split("<Width>"))[1].split("</Width>")[0]
    except:
        logging.error("MEDIAINFO ERROR: Could not parse Frame Width for " + airtable_update_dict[config.FILENAME])
    try:
        frame_height = (mi_Video_Text.split("<Height>"))[1].split("</Height>")[0]
    except:
        logging.error("MEDIAINFO ERROR: Could not parse Frame Height for " + airtable_update_dict[config.FILENAME])

    airtable_update_dict[config.VIDEO_FRAME_SIZE] = frame_width + "x" + frame_height

    try:
        airtable_update_dict[config.VIDEO_ASPECT_RATIO] = (mi_Video_Text.split("<DisplayAspectRatio_String>"))[1].split("</DisplayAspectRatio_String>")[0]
    except:
        print("MEDIAINFO ERROR: Could not parse Display Aspect Rastio for " + airtable_update_dict[config.FILENAME])

        # Audio Stuff
    try:
        airtable_update_dict[config.AUDIO_SAMPLING_RATE] = (mi_Audio_Text.split("<SamplingRate>"))[1].split("</SamplingRate>")[0]
    except:
        logging.error("MEDIAINFO ERROR: Could not parse Audio Sampling Rate for " + airtable_update_dict[config.FILENAME])
    try:
        airtable_update_dict[config.AUDIO_CODEC] = (mi_Audio_Text.split("<Codec>"))[1].split("</Codec>")[0]
    except:
        try:
            airtable_update_dict[config.AUDIO_CODEC] = (mi_Audio_Text.split("<Format>"))[1].split("</Format>")[0]
        except:
            logging.error("MEDIAINFO ERROR: Could not parse Audio Track Encoding for " + airtable_update_dict[config.FILENAME])

    return airtable_update_dict



# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
