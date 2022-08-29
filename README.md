# Charya-Burt-Cambodian-Dance-Digital-Legacy-Library

## Software and Setup

### Software (install in the following order)

* Homebrew
  - Install with the following command: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
* Python 3
  - Install with the following command: `brew install python3`
* Mediainfo
  - Install with the following command: `brew install mediainfo`
* youtube-dl
   - Install with the following command: `brew install youtube-dl`
* FFmpeg
  - Install with the following command:  `brew install ffmpeg`
* Gdrive
 - Install with the following command:  `brew install gdrive`

### Python Libraries

* Airtable:
  - Install with the following command: `pip3 install airtable-python-wrapper`
* Vimeo:
  - Install with the following command: `pip3 install PyVimeo`

### API Credentials

You'll need to get API logins and credentials from Airtable and Vimeo.

Rename `config_template.py` to `config.py` and then fill out the credentials from the API websites

Airtable: https://support.airtable.com/hc/en-us/articles/219046777-How-do-I-get-my-API-key-
Vimeo: https://developer.vimeo.com/apps

### Configuration File

This repository comes with a files named `config_template.py`. This is a template for a configuration files, which you'll need to fill out in order to get the Airtable and Vimeo APIs working properly. Make sure that any info you enter into the configuration file is in double quotes, and follows that formatting of the information that's already in there.

Before you can run any of the scripts you'll need to rename `config_template.py` to `config.py` then fill out the empty fields discussed below.

#### General Config Info

This section contains general configuration info.

- *DRIVE_NAME*: This is the name of the drive that the local repository lives on.
- *BACKUP_DRIVE_NAME*: If you want to run `backup_drive.sh` the backup will run from the main drive to whatever drive name you put here.

_NOTE_: If you switch out drives during backup cycles make sure you update the `DRIVE_NAME` field. This field is critical for performing drive and access maintenance.

#### Airtable Credentials and Config

- *BASE_ID This is the ID for the Base that your Airtable lives in. You can get this from XXXX
- *API_KEY*: To get an API key for Airtable you'll need to go to XXXX

#### Vimeo Credentials

- *YOUR_ACCESS_TOKEN*: Get the Vimeo Access Token from XXXX`
- *YOUR_CLIENT_ID*: Get the Vimeo Client ID token from XXXX
- *YOUR_CLIENT_SECRET*: Get the Vimeo Client Secret token from XXXX
- *VIMEO_DEFAULT_DESCRIPTION*: You can create a default description that will be appended to the Vimeo description of every file.

#### Google Drive Config

- *GDRIVE_LINK_TEXT*: This is the text that will go into the field named "Access Link" for files on the Google Drive. It's basically a manual redirect because there's not simple way to password protect a google drive file (for now)
- *GDRIVE_ROOT_ID*: This is the ID of the folder in your Google Drive that all the files will be uploaded to. To get the ID go to the folder you want and copy the string of letters after the last slash in the URL. For example, if the URL is `https://drive.google.com/drive/u/2/folders/a1b2n3m4g5v6j76liksdpe4` then the id is `a1b2n3m4g5v6j76liksdpe4`

#### Dependency Paths

This information comes pre-filled, and should match up with where homebrew installs each application. However, if these applications won't run you can open a terminal window and run the `which` command to see where the current location of each application is.

For example, to find the path of ffmpeg you can run `which ffmpeg` which will return `/usr/local/bin/ffmpeg`. You can then copy and paste `/usr/local/bin/ffmpeg` into the `FFMPEG_PATH` field in the config file.

####Various Hardcoded Values

For now the only hardcoded value is `MAX_SIZE`, which defines how large a file can be before it will have a downscaled access copy created. This is in order to get around Vimeo's size and upload limits. This field is in bytes, so 5000000000 is equal to 5GB.

#### Airtable Field References

This section is prefilled to work with the template version of the Airtable. If you decide you'd like to change field name in the Airtable make sure to change the field name here as well. This is how the python scripts know the names of the fields in Airtable.

## Scripts

### recordMaintenance.py

This script is used to update records and perform the regular maintenance required for long-term preservation. It can be run with different flags in order to run specific subprocesses. No matter which flags are used the script will perform three audits before any extra subprocesses can be run:

- *Drive Audit*: This checks every record/folder on the drive and makes sure that it has a corresponding active (non-deaccessioned) Airtable record.
- *Airtable Audit*: This checks every active record on the Airtable and makes sure that it has a corresponding folder on the drive.
- *File Audit*: This checks every file record related to an active record on the Airtable and makes sure that it appears on the drive in the location that Airtable thinks it should be.

If any of these three audits fail, the script will ask you to fix the problems before you continue. It it possible to skip the audits, but it is HIGHLY recommended that you not do so, since updating an out of sync drive or Airtable can cause more problems in the future.

### accessMaintenance.py

This script is used to sync the Airtable, Drive, and Vimeo together. It can be run with different flags in order to run specific subprocesses. Like the record maintenance script, this script will run a drive, airtable, and file audit before doing anything else. It will not let you upload anything if these audits fail.


- `-ua [Quantity]`, or `--Upload-Access [Quantity]` Runs the Access Upload sub-process. By default this will upload the first 5 files it finds that need to be uploaded to their associated Access Platform. If you put a number after the -uv (quantity) flag it will upload that number of files that it finds. The script asks Airtable whether the file belongs on Google Drive or Vimeo and uploads accordingly. For now there's no way to upload only Google Drive or Only Vimeo. The script will essentially go through anything that needs to be uploaded at random and start uploading it.

- `-sv` or `--Sync-Vimeo` Runs the Sync Vimeo sub-process. This runs through the entire Airtable and updates the Title and Description of every file on Vimeo. This should be run once a month or so to make sure that the Vimeo pages are sync'd up with the Airtable records

## Performing Regular Maintenance
