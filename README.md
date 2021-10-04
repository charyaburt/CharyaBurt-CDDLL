# Charya-Burt-Cambodian-Dance-Digital-Legacy-Library

## Required Dependencies

### Software

- Mediainfo
- FFmpeg

### Python Libraries

- Airtable: `pip3 install airtable-python-wrapper`

## Scripts

### recordMaintenance.py

This script is used to update records and perform the regular maintenance required for long-term preservation. It can be run with different flags in order to run specific subprocesses. No matter which flags are used the script will perform an audit of the drive against the Airtable, throwing errors if it cannot find the folder of any record.

- `-gf` or `--Get-Filename`: This subprocess will use the "Unique ID" and "Group" fields from Airtable to find the directory where the file lives. It will then harvest the file name of the FIRST file in the folder alphabetically. This script will only affect records with no filename in Airtable, and thus should generally only by run when adding new files to the library.
- `-gc` or `--Get-Checksums`: This subprocess will use the "Unique ID", "Group", and "File Name" fields to find the path to a file. It will then create an MD5 checksum for this file and enter that info into the Checksum field.
- `-vc` or `--Validate-Checksums`: This subprocess will validate checksums. It will skip any records with no checksums already in Airtable. Upon validation the script will update the "Checksum Valid" field to "Yes" upon success, and "No" upon failure. It will also update the "Last Checksum Validated Date" with the current date.
