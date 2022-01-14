# Charya-Burt-Cambodian-Dance-Digital-Legacy-Library

## Required Dependencies

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

## Scripts

### recordMaintenance.py

This script is used to update records and perform the regular maintenance required for long-term preservation. It can be run with different flags in order to run specific subprocesses. No matter which flags are used the script will perform an audit of the drive against the Airtable, throwing errors if it cannot find the folder of any record.

- `-h` or `--help`: This runs the help command, which shows all the available runtime flags. These flags are listed and described in more detail below.
- `-v` or `--verbose`: Defines verbose level for standard out (stdout). v = WARNING, vv = INFO, vvv = DEBUG. All of this output will always be visible in the log, so this isn't super useful if you're looking at the log all the time, which you should be!
- `-gf` or `--Get-Filename`: This subprocess will use the "Unique ID" and "Group" fields from Airtable to find the directory where the file lives. It will then harvest the file name of the FIRST file in the folder alphabetically. This script will only affect records with no filename in Airtable, and thus should generally only by run when adding new files to the library.
- `-gc` or `--Get-Checksums`: This subprocess will use the "Unique ID", "Group", and "File Name" fields to find the path to a file. It will then create an MD5 checksum for this file and enter that info into the Checksum field.
- `-vc` or `--Validate-Checksums`: This subprocess will validate checksums. It will skip any records with no checksums already in Airtable. Upon validation the script will update the "Checksum Valid" field to "Yes" upon success, and "No" upon failure. It will also update the "Last Checksum Validated Date" with the current date.
- `-dv` or `--Download-Vimeo` Runs the Vimeo Download subcprocess. This will download a file from Vimeo and put it in the proper folde ron the drive.
- `-uv [Quantity]`, or `--Upload-Vimeo [Quantity]` Runs the Vimeo Upload subcprocess. By default this will upload the first 5 files it finds that need to be uploaded to Vimeo. If you put a number after the -uv (quantity) flag it will upload that number of files that it finds
- `-fa`, `--File-Audit` Runs a file-level audio subcprocess. This is more detailed than the auto-audio, which only checks that the Unique ID folders exist. This checks that files exist as well
- `-ad`, `--Auto-Deaccession` Runs the auto-deaccession subcprocess. This moves all records marked "Not in Library" to a _Trash folder. This should be run on a regular basis to ensure that junk files aren't sitting around.
- `-f [record ID]`, or `--Find F`  Runs the find subcprocess. This returns the path of whatever record is searched for


#### Record Maintenance Hints, Tips, and Best Practices

- Record Maintenance will ALWAYS run a record-level audit when you run it. This is the first thing it does. It will quit if the audit fails. The audit will fail if a record labeled On Library and On Drive is not found on the drive. If the script fails you should immediately figure out what's missing and get it back on the drive, either from a backup or from vimeo using the `-dv` flag.
- Record Maintenance can be run with multiple fl
- Record Maintenance will warn you if your records are missing filenames or checksums. It is ok for records to missing this information sometimes, like if the record has just been added or the file was just recently downloaded from vimeo. If you get warnings that these are missing for some records your best bet is to run the script with both the `-gf` and `-gc` flags (in that order).
- File Audit will look to see if every file listed in airtable can be found on the drive. If it finds multiple files in the drive folder it will be upset, unless you have an access copy name listed in airtable. The idea here is that if you need to make an access copy it will be ok for there to be more than one file in the folder, but you need to make sure you put the access copy filename in airtable. This will ensure that the vimeo uploader picks the correct file.
