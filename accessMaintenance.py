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
    #parser.add_argument('-dv', '--Download-Vimeo',dest='dv',action='store_true',default=False,help="Runs the Vimeo Download subcprocess. This likely won't ever actually need to be run if the archive is being properly maintained")
    parser.add_argument('-sv', '--Sync-Vimeo',dest='sv',action='store_true',default=False,help="Runs the Sync Vimeo subcprocess. This syncs all the airtable info (description, password, etc) to the current Vimeo page")
    parser.add_argument('-ua', '--Upload-Access',dest='ua',nargs='?',type=int,default=0,const=5,help="Runs the Vimeo Upload subcprocess. By default this will upload the first 5 files it finds that need to be uploaded to Vimeo. If you put a number after the -ua flag it will upload that number of files that it finds. Uploader will only update files with set to 'Vimeo' in the Online Platform field")
    args = parser.parse_args()

    if args.d:
        log_level=logging.DEBUG
    else:
        log_level=logging.INFO

    levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]     #The default verbosity level for stdout is CRITICAL
    verbose_level = levels[min(len(levels)-1,args.verbose)]

    logDir = os.getcwd()               # The log will be created at the working directory
    logName = 'accessMaintenance_' + datetime.today().strftime('%Y-%m-%d')  # The script will be named log.log
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

    drive_name=config.DRIVE_NAME

    #skip audits if run with -sa flag
    if not args.sa:

        #similar to record maintenance, the airtable and drive must pass audits before any vimeo maintenance can occur
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


    #Perform Download Vimeo subprocess
    #if args.dv:
    #    downloadVimeo(airtable, drive_name)

    #needs to be moved to a vimeo maintenance script
    #Perform Upload Vimeo subprocess
    if args.ua > 0 or args.sv:
        v = connectToVimeo(config.YOUR_ACCESS_TOKEN, config.YOUR_CLIENT_ID, config.YOUR_CLIENT_SECRET)

        if v == False:
            quit()

        if args.ua > 0:
            uploadAccessSubprocesses(v, args.ua)

        if args.sv:
            syncVimeo(v)

    logging.critical('========Script Complete========')

## End of main function

#pres_mediainfo_dict = parseMediaInfo(pres_file_path, pres_mediainfo_text, record_dict_entry['RID'], record_dict_entry['record_id'])

def createVimeoDict(upload_files_dict):
    # THIS IS WHERE WE CREATE THE DICTIONARY THAT WILL UPLOAD THE FILES TO VIMEO
    if upload_files_dict['airtable_vimeo_access'] == "Public":
        vimeoDict = {'name': upload_files_dict['name'], 'description': upload_files_dict['description'], 'privacy':{'view' : 'anybody'}}
    elif upload_files_dict['airtable_vimeo_access'] == "Only Me":
        vimeoDict = {'name': upload_files_dict['name'], 'description': upload_files_dict['description'], 'privacy':{'view' : 'nobody'}}
    elif upload_files_dict['airtable_vimeo_access'] == "Private":
        vimeoDict = {'name': upload_files_dict['name'], 'description': upload_files_dict['description'], 'privacy':{'view' : 'password'}, 'password': upload_files_dict['password']}
    else:       # if for some reason there's not a permission listed, we'll make it have the default password: Charya#1dance
        vimeoDict = {'name': upload_files_dict['name'], 'description': upload_files_dict['description'], 'privacy':{'view' : 'password'}, 'password': 'Charya#1dance'}

    return vimeoDict

def checkForAccessFile(mediainfo_dict):
    reason_list = []
    if "Interlaced" in mediainfo_dict[config.VIDEO_SCAN_TYPE]: #needs access file if it's interlaced
        reason_list.append("Interlaced")
    if int(mediainfo_dict[config.FILE_SIZE]) > config.MAX_SIZE: #needs access file if it's too big
        reason_list.append("Large")
    if mediainfo_dict['file_type'] == "Audio": #needs to have an access file made becuase it's just audio
        reason_list.append("No Video")
    return reason_list

def createAccessFile(filePath, mediainfo_dict, reason_list, RID):
    #creates access file. returns access file path
    fileNameExtension = filePath.split(".")[-1]
    accessFilePath = filePath.split("." + fileNameExtension)[0] + "_access.mp4"
    if mediainfo_dict[config.VIDEO_ASPECT_RATIO] == "None":
        aspect_string = ""
    else:
        aspect_string = "-aspect " + mediainfo_dict[config.VIDEO_ASPECT_RATIO]

    ffmpeg_base = config.FFMPEG_PATH + " -hide_banner -loglevel panic -i "
    ffmpeg_middle = ""
    if "No Video" in reason_list:
        logging.info('File in record %s, named %s has no video, creating a video version for access file.' % (RID, mediainfo_dict[config.FILENAME]))
        ffmpeg_middle = "-filter_complex '[0:a]showwaves=s=640x480,format=yuv420p[vid]' -map '[vid]' -map 0:a -codec:v libx264 -crf 25 -preset fast -codec:a aac -strict -2 -b:a 192k -y"
    elif "Interlaced" in reason_list and "Large" in reason_list:
        logging.info('File in record %s, named %s is Interlaced and over 5GB. Making a smaller Progressive access file' % (RID, mediainfo_dict[config.FILENAME]))
        ffmpeg_middle = "-c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -vf yadif -s 640x480 %s -y" % aspect_string
    elif "Interlaced" in reason_list:
        logging.info('File in record %s, named %s is Interlaced. Making a Progressive access file' % (RID, mediainfo_dict[config.FILENAME]))
        ffmpeg_middle = "-c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -vf yadif -y"
    elif "Large" in reason_list:
        logging.info('File in record %s, named %s is larger than max limit (%i Bytes). Making a smaller access file' % (RID, (mediainfo_dict[config.FILENAME]), config.MAX_SIZE))
        ffmpeg_middle = "-c:v libx264 -pix_fmt yuv420p -movflags faststart -crf 18 -s 640x480 %s -y" % aspect_string


    ffmpeg_string = "%s '%s' %s '%s'" %(ffmpeg_base, filePath, ffmpeg_middle, accessFilePath)
    logging.info("Running FFmpeg command: %s" % ffmpeg_string)
    cmd = [ffmpeg_string]
    ffmpeg_out = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
    logging.info("Finished Running FFmpeg command")
    return accessFilePath
    #ffmpeg -i input.mp4 -filter_complex "[0:a]showwaves=s=1280x720,format=yuv420p[vid]" -map "[vid]" -map 0:a -codec:v libx264 -crf 18 -preset fast -codec:a aac -strict -2 -b:a 192k output.mp4

def uploadRecordToGdrive(g_dict, counter_dict):

    #{'record_id' : record_id, 'RID' : RID, 'file_path': file_path, 'airtable_gdrive_access' : airtable_gdrive_access, 'password' : airtable_gdrive_password}

    #first we make the directory with the record number ID in google drive
    #this gives us back the google drive ID
    try:
        logging.info('Creating folder named: %s to Google Drive' % g_dict['RID'])
        mkdir_cmd = [ config.GDRIVE_PATH + " mkdir -p " + config.GDRIVE_ROOT_ID + " " + g_dict['RID'] ]
        gdrive_mkdir_out = subprocess.Popen(mkdir_cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
        gdrive_mkdir_out = gdrive_mkdir_out.decode()
    except Exception as e:
        logging.error('Error creating folder named: %s to Google Drive' % g_dict['RID'])
        logging.error(e)
        counter_dict['error_counter'] += 1
        return counter_dict

    new_folder_id = gdrive_mkdir_out.split(" ")[1] #second word in output will be the id of the new folder

    #Next we upload the file or folder in the record directory to google drive
    try:
        logging.info('Uploading files to Google Drive folder: %s' % g_dict['RID'])
        upload_cmd = [ config.GDRIVE_PATH + " upload -p " +  new_folder_id + " -r '" + g_dict['file_path'] + "'" ]
        gdrive_upload_out = subprocess.Popen(upload_cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
        gdrive_upload_out = gdrive_upload_out.decode()
        logging.info('Finished uploading files to Google Drive folder: %s' % g_dict['RID'])
        counter_dict['upload_counter'] += 1
    except Exception as e:
        logging.error('Error Uploading files to Google Drive folder: %s' % g_dict['RID'])
        logging.error(e)
        counter_dict['error_counter'] += 1
        return counter_dict

    #if that's succesfull then we get info of the uploaded folder to get the url
    try:
        info_cmd = [ config.GDRIVE_PATH + " info " +  new_folder_id ]
        gdrive_info_out = subprocess.Popen(info_cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
        gdrive_info_out = gdrive_info_out.decode()
    except Exception as e:
        logging.info('Error harvesting Google Drive info from: %s' % g_dict['RID'])
        logging.error(e)
        counter_dict['error_counter'] += 1
        return counter_dict

    new_folder_view_url = gdrive_info_out.split("ViewUrl: ")[1].rstrip() #second word in output will be the id of the new folder
    update_dict = {config.ACCESS_LINK : config.GDRIVE_LINK_TEXT, config.ACCESS_LINK : new_folder_view_url, config.ACCESS_PLATFORM_ID : new_folder_id, config.ACCESS_PERMISSION : g_dict['airtable_gdrive_access'], config.ACCESS_PASSWORD : ""}

    #lastly we update airtable with the ID and URL. awesome!
    try:
        airtable = Airtable(config.BASE_ID, 'Records', config.API_KEY)
        airtable.update(g_dict['record_id'], update_dict)
        logging.info('Succesfully added Google Drive link for record %s ' % g_dict['RID'])
        counter_dict['update_counter'] += 1
    except Exception as e:
        logging.error('Could not added Google Drive link for record %s' % g_dict['RID'])
        logging.error('%s' % e)
        counter_dict['error_counter'] += 1

    return counter_dict

def uploadFileToVimeo(v, vimeoDict, file_path, vimeo_upload_files_dict, counter_dict):

    try:
        logging.info('Uploading file: %s to Vimeo' % file_path)
        video_uri = v.upload(file_path,data=vimeoDict)
        logging.info('Upload complete')
        video_data = v.get(video_uri + '?fields=link').json()
        vimeo_link = video_data['link']
        update_dict = {config.ACCESS_LINK : vimeo_link, config.ACCESS_PLATFORM_ID : video_uri, config.ACCESS_PERMISSION : vimeo_upload_files_dict['airtable_vimeo_access'], config.ACCESS_PASSWORD : vimeo_upload_files_dict['password']}
        counter_dict['upload_counter'] += 1
        if "_access" in file_path:  #need to delete acccess file after uploading it
            try:
                os.remove(file_path)
                logging.info('Succesfully deleted access file: %s ' % file_path)
            except Exception as e:
                logging.error('Error deleting access file: %s ' % file_path)
    except Exception as e:
        logging.error('Could not upload file to Vimeo for record %s.' % vimeo_upload_files_dict['RID'])
        logging.error(e)
        if "_access" in file_path:  #need to delete acccess file if there's an error or else we'll have left over access files.
            try:
                os.remove(file_path)
                logging.info('Succesfully deleted access file: %s ' % file_path)
            except Exception as e:
                logging.error('Error deleting access file: %s ' % file_path)
        counter_dict['error_counter'] += 1
        if "Your account doesn't have enough free space to upload this video" in str(e):       #if vimeo returns an error about reaching upload limits then we need to quit the script.
            counter_dict['status'] = False
            return counter_dict                #returning with counter_dict status as false triggers the script to break the for loop that uploads vimeo files

    #THIS IS THE IMPORTANT BIT WHERE WE UPDATE THE TABLE!
    try:
        airtable = Airtable(config.BASE_ID, 'Records', config.API_KEY)
        airtable.update(vimeo_upload_files_dict['record_id'], update_dict)
        logging.info('Succesfully added Vimeo link for record %s ' % vimeo_upload_files_dict['RID'])
        counter_dict['update_counter'] += 1
    except Exception as e:
        logging.error('Could not added Vimeo link for record %s' % vimeo_upload_files_dict['RID'])
        logging.error('%s' % e)
        counter_dict['error_counter'] += 1

    return counter_dict



def connectToVimeo(c_token, c_key, c_secret):
    v = vimeo.VimeoClient(token=c_token, key=c_key, secret=c_secret)

    ## Make the request to the server for the "/me" endpoint.
    about_me = v.get('/me')

    ## Make sure we got back a successful response.
    try:
        assert about_me.status_code == 200
    except Exception as e:
        logging.error('Quitting script. Cannot connect to Vimeo: %s' % e)
        return False

    return v

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
            try:
                record_status = record['fields'][config.RECORD_STATUS]
            except Exception as e:
                record_status = "None"  #it is worth noting and telling the user if a file doesn't have a status
            if record_status != config.RECORD_DEACCESS_FLAG:     #only process records that are in the library
                RID = record['fields'][config.RECORD_NUMBER]
                path = os.path.join('/Volumes', drive_name, RID)    #will need to fix this to make it cross platform eventually
                if not os.path.isdir(path):
                    logging.error('Could not find folder for record %s on drive named %s' % (RID, drive_name))
                    missing_from_drive_count += 1
                else:
                    correct_on_drive_count += 1
                if record_status == "None":
                    no_status += 1
                    logging.warning('Record %s has no status. Please enter a status for this record.' % RID)

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
        print('ERROR: This script has found %i record(s) on the drive marked as "Not In Library" in Airtable. Please consult the log and fix this problem before continuing.' % in_airtable_not_in_library)
        logging.error('This script identified %i record(s) on the drive marked as "Not In Library" in Airtable. Please fix this before continuing.' % in_airtable_not_in_library)
    if missing_from_airtable_count == 0 and in_airtable_not_in_library == 0:
        print('Record level Airtable audit completed succesfully, no errors found. %i record(s) were succesfully located.' % in_airtable_and_in_library)
        logging.info('Record level Airtable audit completed succesfully, no errors found. %i record(s) were succesfully located.' % in_airtable_and_in_library)
        return True
    else:
        logging.info('Record level Airtable audit complete with errors, %i record(s) were succesfully located' % in_airtable_and_in_library)
        return False

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
                file_record_id = file['id']
                RID = file['fields'][config.RECORD_NUMBER_LOOKUP][0]
                try:                                        #checks to see if record has an entry in the File Name field. This will only process empty file names, so as not to overwrite
                    airtable_filename = file['fields'][config.FULL_FILE_NAME]
                except Exception as e:
                    logging.error('Error retreiving file name for record %s. Please fix this record and continue' % RID)
                    error_count += 1
                file_path = os.path.join('/Volumes', drive_name, RID, airtable_filename)    #will need to fix this to make it cross platform eventually
                if os.path.isfile(file_path):
                    file_found_counter += 1
                elif os.path.isdir(file_path):
                    file_found_counter += 1
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
                #    logging.warning('Multiple files found in ' + RID + ' but no access copy listed in Airtable, using ' + files_list[0])
                #    if airtable_filename != files_list[0]:
                #        missing_file_counter += 1
                #        logging.error('Filename Mismatch for record %s. Please fix this before continuing' % RID)
                #if len(files_list) == 0:
                #    logging.error('No files found in %s' % RID)
                #    missing_file_counter += 1
                #else:
                #    if airtable_filename != files_list[0]:
                #        missing_file_counter += 1
                #        logging.error('Filename Mismatch for record %s. Please fix this before continuing' % RID)

    logging.info('File-level audit complete, %i errors found.' % error_count)
    return

def downloadVimeo(airtable, drive_name):
    print('Performing the Download Vimeo subprocess')
    logging.info('Performing the Download Vimeo subprocess')
    success_counter = 0
    warning_counter = 0
    error_counter = 0
    pages = airtable.get_iter()
    for page in pages:
        for record in page:
            RID = record['fields']['Unique ID']
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
                        logging.warning('Record ' + RID + ' Marked as In Library and Not On Drive, but no Vimeo Link found. Skipping')
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
                        logging.info('Downloading file from Vimeo: %s' % RID)
                    try:                                        #Need to have an try/except here because airtable errors if the field is empty. This is in case there is no Group
                        group = record['fields']['Group']
                    except Exception as e:
                        group = ""
                    if group == "":                             #In case there is no Group, we don't want an extra slash
                        path = os.path.join('/Volumes', drive_name, RID)    #will need to fix this to make it cross platform eventually
                    else:
                        path = os.path.join('/Volumes', drive_name, group, RID)    #will need to fix this to make it cross platform eventually
                    if not os.path.isdir(path):     #see if record path exists, if not make it
                        os.makedirs(path, exist_ok=False)
                        logging.info('Folder for %s created', RID)
                    ydl_command = "youtube-dl -f best -o '" + path + "/%(title)s.%(ext)s' --video-password '" + vimeoPassword + "' " + vimeoLink
                    return_code = subprocess.call(ydl_command, shell=True)
                    if return_code == 0: #success
                        logging.info('Succesfully downloaded file from Vimeo: %s' % RID)
                        update_dict = {'On Drive': "Yes"}
                        try:
                            airtable.update(record_id, update_dict)
                            logging.info('Succesfully updated On Drive to Yes for record %s ' % RID)
                            success_counter += 1
                        except Exception as e:
                            logging.warning('Could not update On Drive field for record %s. Please do this manually!' % RID)
                            warning_counter += 1
                    elif return_code == 1: #fail
                        logging.info('Failed to download file from Vimeo: %s' % RID)
                        error_counter += 1
                    else:                   #idk if this is possible, but putting it in here anyway just in case
                        logging.warning('Something strange happened when trying to download the file from Vimeo: %s' % RID)
                        warning_counter += 1
                    #print(ydl_command) #GOTTA TEST THIS
                else:   #ignore if record is already  "On Drive"
                    continue
            else:   #ignore if record is not "In Library"
                continue

    logging.info('Vimeo download complete, %i files downloaded, %i warnings encountered, %i errors found.' % (success_counter, warning_counter, error_counter))
    return


def syncVimeo(v):
    # syncs vimeo to airtable data
    # Uses title and info card to fill out the vimeo details
    #MEDIA_TYPE = "Media Type"
    #ONLINE_PLATFORM = "Online Platform"
    drive_name = config.DRIVE_NAME
    logging.info('Preparing videos to update/sync')
    update_counter = 0
    upload_counter = 0
    warning_counter = 0
    error_counter = 0
    update_vimeo_dict_list = []
    pages = getAirtablePages("Records")
    airtable_files = Airtable(config.BASE_ID, 'Files', config.API_KEY)
    for page in pages:
        for record in page:
            try:
                record_status = record['fields'][config.RECORD_STATUS]
            except Exception as e:
                record_status = "None"
            if record_status != config.RECORD_DEACCESS_FLAG:     #only process records that are in the library
                record_id = record['id']
                RID = record['fields'][config.RECORD_NUMBER]
                try:
                    media_type = record['fields'][config.MEDIA_TYPE]
                except Exception as e:
                    media_type = "none"
                try:
                    online_platform = record['fields'][config.ONLINE_PLATFORM]
                except Exception as e:
                    online_platform = "none"
                try:        #checks to see if record has a vimeo link. If not we skip it
                    airtable_vimeo_link = record['fields'][config.ACCESS_LINK]
                    vimeo_uri = "/videos/" + airtable_vimeo_link.split("/")[-1]
                except Exception as e:
                    continue
                if online_platform == "Vimeo":
                    # This section harvests info from airtable to populate the vimeo record
                    try:
                        airtable_vimeo_access = record['fields'][config.ACCESS_PERMISSION]
                    except:
                        airtable_vimeo_access = "Private"
                    try:
                        airtable_title = record['fields'][config.RECORD_TITLE]
                    except:
                        airtable_title = ""
                    try:
                        full_description = record['fields'][config.INFO_CARD]   #if the info card is empty we skip the record, because otherwise the description will be empty
                    except:
                        logging.warning('Info card for record %s if empty. Skipping record.' % RID)
                        continue
                    try:
                        airtable_vimeo_password = record['fields'][config.ACCESS_PASSWORD]
                    except:
                        if airtable_vimeo_access == "Private":
                            airtable_vimeo_password = "Charya#1dance"
                        else:
                            airtable_vimeo_password = ""

                    update_vimeo_dict = {'record_id' : record_id, 'RID' : RID, 'vimeo URI': vimeo_uri, 'airtable_vimeo_access' : airtable_vimeo_access, 'name': airtable_title, 'description': full_description, 'password' : airtable_vimeo_password}
                    #Append vimeoDict to the end of the list of dicts. We'll then run through the dict later to upload
                    update_vimeo_dict_list.append(update_vimeo_dict)
                    update_counter += 1

    logging.info("Preparing to update/sync %i Vimeo entires" % update_counter)

    updateVimeoPage(v, update_vimeo_dict_list)

    return

def updateVimeoPage(v, update_vimeo_dict_list):

    sync_counter = 0
    error_counter = 0
    #airtable = Airtable(config.BASE_ID, 'Records', config.API_KEY)     #commented out because it was just used by dev to update link and URI fields, but it might be helpful in the future
    update_vimeo_dict_list_sorted = sorted(update_vimeo_dict_list, key=lambda d: d['RID'])
    for upload_files_dict in update_vimeo_dict_list_sorted:

        if upload_files_dict['airtable_vimeo_access'] == "Public":
            vimeoDict = {'name': upload_files_dict['name'], 'description': upload_files_dict['description'], 'privacy':{'view' : 'anybody'}}
        elif upload_files_dict['airtable_vimeo_access'] == "Only Me":
            vimeoDict = {'name': upload_files_dict['name'], 'description': upload_files_dict['description'], 'privacy':{'view' : 'nobody'}}
        elif upload_files_dict['airtable_vimeo_access'] == "Private":
            vimeoDict = {'name': upload_files_dict['name'], 'description': upload_files_dict['description'], 'privacy':{'view' : 'password'}, 'password': upload_files_dict['password']}
        else:       # if for some reason there's not a permission listed, we'll make it have the default password: Charya#1dance
            vimeoDict = {'name': upload_files_dict['name'], 'description': upload_files_dict['description'], 'privacy':{'view' : 'password'}, 'password': 'Charya#1dance'}

        logging.info("Updating Vimeo page for record: %s" % upload_files_dict['RID'])
        try:
            v.patch(upload_files_dict['vimeo URI'], data=vimeoDict)
            logging.info("Finished updating Vimeo page for record: %s" % upload_files_dict['RID'])
            sync_counter += 1
            #commented below out because it was just used by dev to update link and URI fields, but it might be helpful in the future
            #video_data = v.get(upload_files_dict['vimeo URI'] + '?fields=link').json()
            #vimeo_link = video_data['link']
            #update_dict = {config.ACCESS_LINK : vimeo_link, config.ACCESS_PLATFORM_ID : upload_files_dict['vimeo URI']}
            #airtable.update(upload_files_dict['record_id'], update_dict)
        except Exception as e:
            logging.error(e)
            error_counter += 1
            logging.info("Could not update Vimeo page for record: %s" % upload_files_dict['RID'])

    if error_counter > 0:
        logging.error("Finished updating %i Vimeo pages with %i errors" % (sync_counter, error_counter))
    else:
        logging.info("Finished updating %i Vimeo pages without any errors" % sync_counter)

    return

def uploadAccessSubprocesses(v, quantity):
    # Uploads videos from airtable records to vimeo
    # Uses the description, title, location, and dancers to fill out the vimeo details
    # You cannot choose a file to upload, the script will simply start uploading them in order as it finds records with "Yes" as Uplaod to Vimeo but not Vimeo Link
    # The script will automatically run on 5 files and then quit, but you can define how many files you want it to run on
    drive_name = config.DRIVE_NAME
    logging.info('Preparing media to upload')
    update_counter = 0
    upload_counter = 0
    vimeo_upload_counter = 0
    gdrive_upload_counter = 0
    warning_counter = 0
    error_counter = 0
    vimeo_upload_files_dict_list = []
    gdrive_upload_files_dict_list = []
    pages = getAirtablePages("Records")
    airtable_files = Airtable(config.BASE_ID, 'Files', config.API_KEY)
    for page in pages:
        for record in page:
            if upload_counter == quantity:
                break
            try:
                record_status = record['fields'][config.RECORD_STATUS]
            except Exception as e:
                record_status = "None"
            if record_status != config.RECORD_DEACCESS_FLAG:     #only process records that are in the library
                record_id = record['id']
                RID = record['fields'][config.RECORD_NUMBER]
                try:
                    media_type = record['fields'][config.MEDIA_TYPE]
                except Exception as e:
                    media_type = "none"
                try:
                    online_platform = record['fields'][config.ONLINE_PLATFORM]
                except Exception as e:
                    online_platform = "none"
                try:                                        #checks to see if record has an entry in the Checksum field. This will only process files with no checksum already, so as not to overwrite
                    airtable_vimeo_link = record['fields'][config.ACCESS_LINK]
                    continue
                except Exception as e:
                    #logging.info('Uploading file to Vimeo for record %s' % RID)
                    pass    #in this case the exception is actually good. if the vimeo link is empty we need to upload to vimeo!
                if online_platform == "Vimeo":
                    try:            #first, see if an access copy filename exists. If it does we're gonna use this instead.
                        airtable_filename_list = record['fields'][config.FILES_IN_RECORD]
                        if len(airtable_filename_list) > 1: #checks to see if more than one file is associated with the record. if so it warns the user and skips the record
                            logging.warning('Found more than one video file assocaited with record for %s. This should not be the case, please fix this.' % RID)
                            warning_counter =+ 1
                            continue
                        else:
                            airtable_filename_id = airtable_filename_list[0]
                            airtable_filename = airtable_files.get(airtable_filename_id)['fields'][config.FULL_FILE_NAME]
                    except Exception as e:
                        if "Album" not in media_type:
                            logging.warning('No file associated with record for %s. Skipping for now, please fix this record.' % RID)
                            warning_counter =+ 1
                        continue

                    #we need to exlude albums and images from the list
                    if media_type == "Video" or media_type == "Audio":
                        pass
                    else:
                        continue

                    file_path = os.path.join('/Volumes', drive_name, RID, airtable_filename)    #will need to fix this to make it cross platform eventually

                    # This section harvests info from airtable to populate the vimeo record
                    try:
                        airtable_vimeo_access = record['fields'][config.ACCESS_PERMISSION]
                    except:
                        airtable_vimeo_access = "Private"
                    try:
                        airtable_title = record['fields'][config.RECORD_TITLE]
                    except:
                        airtable_title = ""
                    try:
                        full_description = record['fields'][config.INFO_CARD]   #if the info card is empty we skip the record, because otherwise the description will be empty
                    except:
                        logging.warning('Info card for record %s if empty. Skipping record.' % RID)
                        continue
                    try:
                        airtable_vimeo_password = record['fields'][config.ACCESS_PASSWORD]
                    except:
                        if airtable_vimeo_access == "Private":
                            airtable_vimeo_password = "Charya#1dance"
                        else:
                            airtable_vimeo_password = ""


                    vimeo_upload_files_dict = {'record_id' : record_id, 'RID' : RID, 'file_path': file_path, 'airtable_vimeo_access' : airtable_vimeo_access, 'name': airtable_title, 'description': full_description, 'password' : airtable_vimeo_password}
                    #Append vimeoDict to the end of the list of dicts. We'll then run through the dict later to upload
                    vimeo_upload_files_dict_list.append(vimeo_upload_files_dict)
                    vimeo_upload_counter += 1
                    upload_counter += 1

                if online_platform == "Google Drive":

                    try:
                        airtable_filename_list = record['fields'][config.FILES_IN_RECORD]
                        if len(airtable_filename_list) > 1: #checks to see if more than one file is associated with the record. if so it warns the user and skips the record
                            logging.warning('Found more than one video file assocaited with record for %s. This should not be the case, please fix this.' % RID)
                            warning_counter =+ 1
                            continue
                        else:
                            airtable_filename_id = airtable_filename_list[0]
                            airtable_filename = airtable_files.get(airtable_filename_id)['fields'][config.FULL_FILE_NAME]
                    except Exception as e:
                        if "Album" not in media_type:
                            logging.warning('No file associated with record for %s. Skipping for now, please fix this record.' % RID)
                            warning_counter =+ 1
                        continue

                    file_path = os.path.join('/Volumes', drive_name, RID, airtable_filename)
                    # This section harvests info from airtable to populate the google drive record

                    try:            #first, see if an access copy filename exists. If it does we're gonna use this instead.
                        airtable_grouping = record['fields'][config.GROUPING]
                    except Exception as e:
                        airtable_grouping = "None"

                    try:
                        airtable_gdrive_access = record['fields'][config.ACCESS_PERMISSION]
                    except:
                        airtable_gdrive_access = "Private"
                    try:
                        airtable_gdrive_password = record['fields'][config.ACCESS_PASSWORD]
                    except:
                        if airtable_gdrive_access == "Private":
                            airtable_gdrive_password = "Charya#1dance"
                        else:
                            airtable_gdrive_password = ""

                    gdrive_upload_files_dict = {'record_id' : record_id, 'RID' : RID, 'file_path': file_path, 'airtable_gdrive_access' : airtable_gdrive_access, 'password' : airtable_gdrive_password}
                    gdrive_upload_files_dict_list.append(gdrive_upload_files_dict)
                    gdrive_upload_counter += 1
                    upload_counter += 1

    logging.info('Completed preparing %i files for upload to Vimeo and %i files/albums for upload to Google Drive. %i warnings encountered' % (vimeo_upload_counter, gdrive_upload_counter, warning_counter))

    #We process gdrive first in case vimeo errors out due to hitting limits
    gdrive_upload_files_dict_list_sorted = sorted(gdrive_upload_files_dict_list, key=lambda d: d['RID'])
    counter_dict = {'upload_counter' : 0, 'error_counter' : 0, 'update_counter': 0}
    for gdrive_upload_files_dict in gdrive_upload_files_dict_list_sorted:
        counter_dict = uploadRecordToGdrive(gdrive_upload_files_dict, counter_dict)
    if gdrive_upload_counter > 0:   #don't display logging if we didn't do any uploading
        logging.info('Gdrive uploading complete. %i file uploaded, %i airtable records updated, %i errors' % (counter_dict['upload_counter'], counter_dict['update_counter'], counter_dict['error_counter']))

    #We process vimeo second
    #but what's missing is a while to properly deal with vimeo's upload limits!
    vimeo_upload_files_dict_list_sorted = sorted(vimeo_upload_files_dict_list, key=lambda d: d['RID'])
    counter_dict = {'upload_counter' : 0, 'error_counter' : 0, 'update_counter': 0, 'status' : True}
    for vimeo_upload_files_dict in vimeo_upload_files_dict_list_sorted:
        mediainfo_text = getMediaInfo(vimeo_upload_files_dict['file_path'])
        mediainfo_dict = parseMediaInfo(vimeo_upload_files_dict['file_path'], mediainfo_text, vimeo_upload_files_dict['name'],vimeo_upload_files_dict['RID'])
        reason_list = checkForAccessFile(mediainfo_dict)    #get a list of reasons for why we need an access copy (if we do)
        if not reason_list:
            logging.info("No access copy needed. Starting Vimeo upload")
            upload_path = vimeo_upload_files_dict['file_path']
        else:
            upload_path = createAccessFile(vimeo_upload_files_dict['file_path'], mediainfo_dict, reason_list, vimeo_upload_files_dict['RID'])
        vimeoDict = createVimeoDict(vimeo_upload_files_dict)
        counter_dict = uploadFileToVimeo(v, vimeoDict, upload_path, vimeo_upload_files_dict, counter_dict)
        if not counter_dict['status']:
            logging.error("Fatal Error! Likely the Vimeo upload quota has been reached. You can keep uploading Google Drive files but you'll need to wait a week to upload any Vimeo files.")
            break

    if vimeo_upload_counter > 0:    #don't display logging if we didn't do any uploading
        logging.info('Vimeo uploading complete. %i file uploaded, %i airtable records updated, %i errors' % (counter_dict['upload_counter'], counter_dict['update_counter'], counter_dict['error_counter']))


def getMediaInfo(filePath):
    cmd = [ config.MEDIAINFO_PATH, '-f', '--Output=XML', filePath ]
    media_info = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
    return media_info

def parseMediaInfo(filePath, media_info_text, fileName, RID):
    # The following line initializes the dict.
    mediainfo_dict = {config.FILENAME: fileName, config.FILE_SIZE : "", config.VIDEO_SCAN_TYPE : "", config.VIDEO_CODEC : "", config.VIDEO_ASPECT_RATIO : "", 'file_type' : ""}
    media_info_text = media_info_text.decode()
    logging.info("Parsing mediainfo for record %s, file: %s" % (RID, mediainfo_dict[config.FILENAME]))
    file_type = None
    file_has_general = False
    file_has_video = False
    file_has_audio = False

    try:
        mi_General_Text = (media_info_text.split("<track type=\"General\">"))[1].split("</track>")[0]
        file_has_general = True
    except:
        logging.error('The file %s is not a properly formed media file. Please check that this file is correct' %  mediainfo_dict[config.FILENAME])
    try:
        mi_Video_Text = (media_info_text.split("<track type=\"Video\">"))[1].split("</track>")[0]
        file_has_video = True
    except:
        file_has_video = False
    try:
        mi_Audio_Text = (media_info_text.split("<track type=\"Audio\">"))[1].split("</track>")[0]
        file_has_audio = True
    except:
        file_has_audio = False
    try:
        mi_Image_Text = (media_info_text.split("<track type=\"Image\">"))[1].split("</track>")[0]
        file_has_image = True
    except:
        file_has_image = False

    if file_has_video and file_has_audio: #Process as video and audio file
        mediainfo_dict['file_type'] = "Video"
    elif file_has_video: #Process as video only
        mediainfo_dict['file_type'] = "Silent_Video"
    elif file_has_audio: #Process as audio only
        mediainfo_dict['file_type'] = "Audio"

    # Get the rest of the mediainfo metadata
    # General Stuff

    try:
        mediainfo_dict[config.FILE_SIZE] = int((mi_General_Text.split("<FileSize>"))[1].split("</FileSize>")[0])
    except:
        logging.error("MEDIAINFO ERROR: Could not parse File Size for " + mediainfo_dict[config.FILENAME])

    # Video Stuff

    if mediainfo_dict['file_type'] == "Video" or mediainfo_dict['file_type'] == "Silent_Video":
        try:
            mediainfo_dict[config.VIDEO_CODEC] = (mi_Video_Text.split("<CodecID>"))[1].split("</CodecID>")[0]
        except:
            try:
                mediainfo_dict[config.VIDEO_CODEC] = (mi_Video_Text.split("<Format>"))[1].split("</Format>")[0]
            except:
                mediainfo_dict[config.VIDEO_CODEC] = "None"
        try:
            mediainfo_dict[config.VIDEO_SCAN_TYPE] = (mi_Video_Text.split("<ScanType_String>"))[1].split("</ScanType_String>")[0]
        except:
            mediainfo_dict[config.VIDEO_ASPECT_RATIO] = "None"
        try:
            mediainfo_dict[config.VIDEO_ASPECT_RATIO] = (mi_Video_Text.split("<DisplayAspectRatio_String>"))[1].split("</DisplayAspectRatio_String>")[0]
        except:
            mediainfo_dict[config.VIDEO_ASPECT_RATIO] = "None"

    else:
        mediainfo_dict[config.VIDEO_CODEC] = "None"


    return mediainfo_dict


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
