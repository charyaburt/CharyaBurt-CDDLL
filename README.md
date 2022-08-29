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


- `-h` or `--help`: This runs the help command, which shows all the available runtime flags. These flags are listed and described in more detail below.
- `-v` or `--verbose`: Defines verbose level for standard out (stdout). v = WARNING, vv = INFO, vvv = DEBUG. All of this output will always be visible in the log, so this isn't super useful if you're looking at the log all the time, which you should be!
- `sa` or `--Skip-Audit`: This skips the three audits that happen when the script is run. We HIGHLY RECOMMEND That you never run with this flag. It is means for development and testing purposes only.
- `-gc` or `--Get-Checksums`: This subprocess will use the `FULL_FILE_NAME` field in the `FILES` table the path to a file. If the `CHECKSUM` field is empty it will then create an MD5 checksum for this file and enter that info into the `CHECKSUM` field.
- `-vc` or `--Validate-Checksums`: This subprocess will validate checksums. It will skip any records with nothing in the `CHECKSUM` field of the `FILES` table. Upon validation the script will update the `CHECKSUM_VALID` field to "Yes" upon success, and "No" upon failure. It will also update the `CHECKSUM_VALID_DATE` with the current date.
- `-ad`, `--Auto-Deaccession` Runs the auto-deaccession subcprocess. This moves all records in the `RECORDS` table marked "DEACCESSIONED RECORD" in the `FILE_PROCESS_STATUS` to a _Trash folder. This should be run on a regular basis to ensure that junk files aren't sitting around.


### vimeoMaintenance.py

This script is used to sync the Airtable, Drive, and Vimeo together. It can be run with different flags in order to run specific subprocesses. Like the record maintenance script, this script will run a drive, airtable, and file audit before doing anything else. It will not let you upload anything if these audits fail.


- `-uv [Quantity]`, or `--Upload-Vimeo [Quantity]` Runs the Vimeo Upload subcprocess. By default this will upload the first 5 files it finds that need to be uploaded to Vimeo. If you put a number after the -uv (quantity) flag it will upload that number of files that it finds


#### Record Maintenance Hints, Tips, and Best Practices

- Record Maintenance will ALWAYS run a record-level audit when you run it. This is the first thing it does. It will quit if the audit fails. The audit will fail if a record labeled On Library and On Drive is not found on the drive. If the script fails you should immediately figure out what's missing and get it back on the drive, either from a backup or from vimeo using the `-dv` flag.
- Record Maintenance can be run with multiple fl
- Record Maintenance will warn you if your records are missing filenames or checksums. It is ok for records to missing this information sometimes, like if the record has just been added or the file was just recently downloaded from vimeo. If you get warnings that these are missing for some records your best bet is to run the script with both the `-gf` and `-gc` flags (in that order).
- File Audit will look to see if every file listed in airtable can be found on the drive. If it finds multiple files in the drive folder it will be upset, unless you have an access copy name listed in airtable. The idea here is that if you need to make an access copy it will be ok for there to be more than one file in the folder, but you need to make sure you put the access copy filename in airtable. This will ensure that the vimeo uploader picks the correct file.
