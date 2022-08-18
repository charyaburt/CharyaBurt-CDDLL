# General Config Info
DRIVE_NAME = ""   #The name of the hard drive the archive is on. This will change if you plug in a backup drive
BACKUP_DRIVE_NAME = "" #The name of the backup drive
TEMP_PREVIEW_PATH = "" #The path to the folder that will temporarily hold preview files

# Airtable Credentials and Config
BASE_ID = ""
API_KEY = ""
#TABLE_NAME = ""    # this isn't quite necessary anymore

# Airtable Field References
IN_LIBRARY = "(Deprecated) In Library"
IN_LIBRARY_LOOKUP = "(Deprecated) In Library"
RECORD_NUMBER = "Record Number"
RECORD_NUMBER_LOOKUP = "Record Number"
FULL_FILE_NAME = "Full File Name"
CHECKSUM = "Checksum"
FILE_PROCESS_STATUS = "File Processing Status"
FILE_INTAKE_FLAG = "Intaking Local Data File" #This flag is for local file intake.
FILE_UPLOAD_FLAG = "Uploading Online Version" #This flag is for online upload.
FILE_DEACCESS_FLAG = "DEACCESSIONING ALL DATA" #This is the File Processing Status flag that marks a record for deaccession.
RECORD_STATUS = "Status"
RECORD_DEACCESS_FLAG = "Deaccessioned Record" #This is the Record Status flag that marks a record for deaccession.
RECORD_STATUS_LOOKUP = "Status (from Part of Record)"

#Both deaccession flags must be in place for the deaccessioning program to proceed.

#Airtable File Metadata Fields
FILENAME = "File Name"
DURATION = "Duration"
FILE_SIZE_STRING = "File Size String"
FILE_SIZE = "File Size Bytes"
FILE_FORMAT = "File Format"
VIDEO_CODEC = "Video Codec"
VIDEO_BIT_DEPTH = "Video Bit Length"
VIDEO_SCAN_TYPE = "Video Scan Type"
VIDEO_FRAME_RATE = "Video Frame Rate"
VIDEO_FRAME_SIZE = "Video Frame Size"
VIDEO_ASPECT_RATIO = "Video Frame Ratio"
AUDIO_SAMPLING_RATE = "Audio Sampling Rate"
AUDIO_CODEC = "Audio Codec"
CHECKSUM = "Checksum"
COPY_VERSION = "Access Copy Version"
#USE_FOR_ACCESS = "Use for Access"  #no longer needed
PARENT_ID = "Part of Record"
FULL_FILE_NAME = "Full File Name"
FILE_COUNT = "Folder File Count"
CHECKSUM_VALID = "Checksum Valid"
CHECKSUM_VALID_DATE = "Checksum Validated Date"

#Various Hardcoded Values
MAX_SIZE = 5000000000

# Vimeo Credentials
YOUR_ACCESS_TOKEN = ""
YOUR_CLIENT_ID = ""
YOUR_CLIENT_SECRET = ""
VIMEO_DEFAULT_DESCRIPTION = ""

# Dependency Paths
FFMPEG_PATH = "/usr/local/bin/ffmpeg"
FFPROBE_PATH = "/usr/local/bin/ffprobe"
MEDIAINFO_PATH = "/usr/local/bin/mediainfo"
PYTHON_PATH = "/usr/local/bin/python3"
DEPENDENCY_PATH = "/usr/local/bin/"
MOGRIFY_PATH = "/usr/local/bin/mogrify"
CONVERT_PATH = "/usr/local/bin/convert"
