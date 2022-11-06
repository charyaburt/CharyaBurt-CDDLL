---
layout: page
title: Access Maintenance
parent: Scripts
---
# Access Maintenance

This is run using the script named `accessMaintenance.py`

This script is used to sync the Airtable, Drive, and Vimeo together. It can be run with different flags in order to run specific subprocesses. Like the record maintenance script, this script will run a drive, airtable, and file audit before doing anything else. It will not let you upload anything if these audits fail.

## Access Maintenance Subprocesses

- `-ua [Quantity]`, or `--Upload-Access [Quantity]` Runs the Access Upload sub-process. By default this will upload the first 5 files it finds that need to be uploaded to their associated Access Platform. If you put a number after the -uv (quantity) flag it will upload that number of files that it finds. The script asks Airtable whether the file belongs on Google Drive or Vimeo and uploads accordingly. For now there's no way to upload only Google Drive or Only Vimeo. The script will essentially go through anything that needs to be uploaded at random and start uploading it.

- `-sv` or `--Sync-Vimeo` Runs the Sync Vimeo sub-process. This runs through the entire Airtable and updates the Title and Description of every file on Vimeo. This should be run once a month or so to make sure that the Vimeo pages are sync'd up with the Airtable records

## Hardcoded Values Airtable Fields Used
The following entries from `config.py` are used in this script. you'll need to update the config file if you've made

### Hardcoded Values:
- `DRIVE_NAME`
- `YOUR_ACCESS_TOKEN`
- `YOUR_CLIENT_ID`
- `YOUR_CLIENT_SECRET`
- `BASE_ID`
- `API_KEY`
- `DRIVE_NAME`
- `MAX_SIZE`
- `MEDIAINFO_PATH`
- `FFMPEG_PATH`

### Airtable Field Names:
- `RECORD_STATUS`
- `RECORD_DEACCESS_FLAG`
- `RECORD_NUMBER`
- `RECORD_STATUS_LOOKUP`
- `RECORD_NUMBER_LOOKUP`
- `FILENAME`
- `FILE_SIZE`
- `VIDEO_CODEC`
- `VIDEO_ASPECT_RATIO`
- `VIDEO_SCAN_TYPE`
- `ACCESS_PLATFORM_ID`
- `ACCESS_PERMISSION`
- `ACCESS_PASSWORD`
- `ACCESS_LINK`
- `GDRIVE_PATH`
- `GDRIVE_ROOT_ID`
- `GDRIVE_LINK_TEXT`
- `FULL_FILE_NAME`
- `MEDIA_TYPE`
- `ACCESS_PLATFORM`
- `ACCESS_LINK`
- `ACCESS_PERMISSION`
- `ACCESS_PASSWORD`
- `RECORD_TITLE`
- `INFO_CARD`
- `FILES_IN_RECORD`
